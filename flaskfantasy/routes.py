import pandas as pd
from flask import render_template, url_for, request, redirect, session, jsonify, flash
from flask_mail import Message

from flaskfantasy import app, db, mail
from flaskfantasy.forms import SettingsForm, ContactForm
from flaskfantasy.models import Adp


def urgency(adp, pick_num, next_pick_in):
    if adp <= pick_num + next_pick_in[pick_num - 1]:
        urg = {'display': 'High', 'urgency': 1}
    elif adp >= pick_num + next_pick_in[pick_num - 1] + next_pick_in[pick_num + next_pick_in[pick_num - 1] - 1]:
        urg = {'display': 'Low', 'urgency': 3}
    else:
        urg = {'display': 'Medium', 'urgency': 2}
    return urg


def ranking(dfDraft, pick_num, next_pick_in):
    dfTopPlayersNextRd = dfDraft.sort_values('adp')
    dfTopPlayersNextRd = dfTopPlayersNextRd.tail(len(dfTopPlayersNextRd) - next_pick_in[pick_num - 1])
    dfTopPlayersNextRd = dfTopPlayersNextRd.groupby('position').head(1)[['player', 'position', 'adp', 'fantasy_points']]
    dict_pos = dict(zip(dfTopPlayersNextRd['position'], dfTopPlayersNextRd['fantasy_points']))
    for key in ['QB', 'RB', 'TE', 'WR']:
        if key not in dict_pos.keys():
            dict_pos[key] = 0
    dfDraft['vor_pts'] = dfDraft.apply(lambda row: row['fantasy_points'] - dict_pos.get(row['position']), axis=1).round(1)
    dfDraft['vor_pct'] = dfDraft.apply(lambda row: 9999.9 if dict_pos.get(row['position']) == 0 else (row['fantasy_points'] - dict_pos.get(row['position'])) / dict_pos.get(row['position']) * 100, axis=1).round(1)
    dfTopPlayersAvail = dfDraft[['player', 'position', 'adp', 'fantasy_points', 'vor_pts', 'vor_pct']]
    dfTopPlayersAvail['urgency'] = dfTopPlayersAvail.apply(lambda x: urgency(x['adp'], pick_num, next_pick_in), axis=1)
    draftdata = dfTopPlayersAvail[['player', 'position', 'fantasy_points', 'vor_pts', 'vor_pct', 'adp', 'urgency']].to_dict(orient='records')
    repldata = dfTopPlayersNextRd[['player', 'position', 'fantasy_points', 'adp']].to_dict(orient='records')   
    return draftdata, repldata


@app.route("/", methods=['GET','POST'])
@app.route("/home", methods=['GET','POST'])
def home():
    return render_template('index.html')


@app.route("/contact", methods=['GET','POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        name = request.form['name']
        email = request.form['email'].lower()
        subject = request.form['subject']
        message = request.form['message']
        msg = Message(subject, recipients=['playergap.app@gmail.com'])
        msg.body = f'{message}\n\n--\n{name}\n{email}'
        mail.send(msg)
        flash('Your message has been sent!', 'success')
        return redirect(url_for('home'))
    return render_template('contact.html', title='Contact', form=form)


@app.route("/settings", methods=['GET', 'POST'])
def settings():
    form = SettingsForm()
    choices = sorted([src.source_name.replace('FantasyPros-', '') for src in Adp.query.with_entities(Adp.source_name).filter(Adp.season==2022, Adp.system=='1-QB', 
        Adp.scoring=='Half-PPR').distinct()], key=str.casefold)
    choices = ['All (Average)'] + choices
    form.adp_source.choices = choices
    if form.validate_on_submit():
        return redirect(url_for('draft'))
    return render_template('settings.html', title='Settings', form=form)


@app.route("/draft", methods=['GET', 'POST'])
def draft():
    if request.method == 'POST':      
        session.clear()
        season = 2022
        system = request.form['system']
        scoring_format = request.form['scoring_format']
        num_teams = int(request.form['num_teams'])
        roster_size = int(request.form['roster_size']) + 2 #Two extra rounds, so we have something to compare to in the last round
        # projections_source = request.form['projections_source']
        adp_source = request.form['adp_source']
        pick_num = 1
        dfRoster = pd.DataFrame(data=[['', '', '', '', '']], columns=['team', 'pick', 'player', 'position', 'fantasy_points'])

        lst_picks_ov = [*range(1, roster_size * num_teams + 1)]
        
        lst_picks = []
        next_pick_in = []    
        for i in range(1, roster_size + 1):
            for j in range(1, num_teams + 1):
                lst_picks.append(str(i) + '.' + str(j))
            next_pick_in += reversed(range(1, num_teams * 2, 2))
        next_pick_in = [num_teams * 2 if n == 1 else n for n in next_pick_in]
        
        team_picking = []
        for j in range(1, roster_size + 1):
            if j % 2 == 0:
                team_picking += reversed(range(1, num_teams + 1))
            else:
                team_picking += range(1, num_teams + 1)
        
        format_values = {'Half-PPR':[0.04, 4, -2, 0.1, 6, 0.5, 0.1, 6, -2],
                         'PPR':     [0.04, 4, -2, 0.1, 6, 1,   0.1, 6, -2],
                         'Non-PPR': [0.04, 4, -2, 0.1, 6, 1,   0.1, 6, -2]}
        
        how_join = 'RIGHT' if system == 'Rookie' else 'LEFT'
        col_join = 'B.player, B.position, A.fantasy_points, B.adp' if system == 'Rookie' else 'A.player, A.position, A.fantasy_points, B.adp'
    
        if adp_source == 'All (Average)':
            adp_query = f"""SELECT A.player, A.position, AVG(A.adp) AS adp
                            FROM adp A
                            INNER JOIN (
                                SELECT source_name, MAX(source_update) AS source_update
                                FROM adp 
                                WHERE season = {season} 
                                AND system = '{system}'
                                AND scoring = '{scoring_format}'
                                GROUP BY source_name
                            ) B
                            ON A.source_name = B.source_name AND A.source_update = B.source_update
                            WHERE season = {season} 
                            AND system = '{system}'
                            AND scoring = '{scoring_format}'
                            GROUP BY A.player, A.position
            """

        else:
            adp_query = f"""SELECT player, position, adp
                             FROM adp
                             WHERE season = {season} 
                             AND system = '{system}'
                             AND scoring = '{scoring_format}'
                             AND source_name = '{adp_source if adp_source in ['FantasyFootballCalculator', 'FantasyPros'] else 'FantasyPros-'+adp_source}'
                             AND source_update = (SELECT MAX(source_update) 
                                                     FROM adp 
                                                     WHERE season = {season} 
                                                     AND system = '{system}'
                                                     AND scoring = '{scoring_format}'
                                                     AND source_name = '{adp_source if adp_source in ['FantasyFootballCalculator', 'FantasyPros'] else 'FantasyPros-'+adp_source}'
                                                 )
            """

        # if system == '1-QB':
        #     adp_query = f""" 
        #     SELECT player, position, AVG(adp) AS adp
        #                     FROM adp
        #                     WHERE system = '{system}'
        #                     AND scoring = '{scoring_format}'
        #                     AND source_name LIKE 'FantasyPros-%'
        #                     AND source_update = (SELECT MAX(source_update) 
        #                                             FROM adp 
        #                                             WHERE system = '{system}'
        #                                             AND scoring = '{scoring_format}'
        #                                             AND source_name LIKE 'FantasyPros-%'
        #                                         )
        #                     GROUP BY player, position
        #                 """
        # elif system == '2-QB':
        #      adp_query = f"""
        #      SELECT player, position, adp
        #                     FROM adp
        #                     WHERE system = '{system}'
        #                     AND scoring = '{scoring_format}'
        #                     AND source_update = (SELECT MAX(source_update) 
        #                                             FROM adp 
        #                                             WHERE system = '{system}'
        #                                             AND scoring = '{scoring_format}'
        #                                         )
        #                 """  
        # else:
        #      adp_query = f"""
        #      SELECT player, position, adp
        #                     FROM adp
        #                     WHERE system = '{system}'
        #                     AND scoring = '{scoring_format}'
        #                     AND source_name = 'FantasyPros'
        #                     AND source_update = (SELECT MAX(source_update) 
        #                                             FROM adp 
        #                                             WHERE system = '{system}'
        #                                             AND scoring = '{scoring_format}'
        #                                             AND source_name = 'FantasyPros'
        #                                         )
        #                 """              

        query = f"""
        SELECT {col_join}
        FROM        
            (SELECT player, position, pass_yd    * {format_values[scoring_format][0]}
                                    + pass_td    * {format_values[scoring_format][1]}
                                    + pass_int   * {format_values[scoring_format][2]}
                                    + rush_yd    * {format_values[scoring_format][3]}
                                    + rush_td    * {format_values[scoring_format][4]}
                                    + receiv_rec * {format_values[scoring_format][5]}
                                    + receiv_yd  * {format_values[scoring_format][6]}
                                    + receiv_td  * {format_values[scoring_format][7]} 
                                    + fumble_lst * {format_values[scoring_format][8]} AS fantasy_points
                        FROM projections
                        WHERE season = {season} 
                        AND source_name = 'FantasyPros'
                        AND position NOT IN ('DST', 'K')
                        AND source_update = (SELECT MAX(source_update) FROM projections WHERE source_name = 'FantasyPros')
            ) A
            {how_join} JOIN
            ({adp_query}
            ) B
            ON (A.player=B.player AND A.position=B.position)
            ORDER BY fantasy_points DESC
                 """
        
        dfDraft = pd.DataFrame(db.session.execute(query), columns=['player', 'position', 'fantasy_points', 'adp'])      
        dfDraft['fantasy_points'] =  dfDraft['fantasy_points'].astype(float).round(1)
        dfDraft['adp'] =  dfDraft['adp'].astype(float).fillna(999.9)
        dfDraft.fillna(0, inplace=True)
        draft_head = ['', 'Player', 'Pos', 'FPts', 'Gap', 'Gap %', 'ADP', 'Urgency']
        repl_head = ['Player', 'Pos', 'FPts', 'ADP']
        team_head = ['Pos', 'Player']
        pick_label = 'Current Pick: ' + lst_picks[pick_num - 1] + ' - #' + str(pick_num) + ' Overall'
        team_label = 'Team ' + str(team_picking[pick_num - 1])
        next_pick_label = 'Next Pick: ' + lst_picks[pick_num + next_pick_in[pick_num - 1] - 1] + ' - #' + str(lst_picks_ov[pick_num + next_pick_in[pick_num - 1] - 1]) + ' Overall'
        prev_pick_label = 'Latest Pick: 0.0'
        prev_team_label = 'Made By: Team 0'
        prev_player_label = 'Player'
        prev_pos_label = 'Position'
        session['pick_num'] = pick_num
        session['lst_picks_ov'] = lst_picks_ov
        session['lst_picks'] = lst_picks
        session['next_pick_in'] = next_pick_in
        session['team_picking'] = team_picking
        session['roster_size'] = roster_size
        session['num_teams'] = num_teams 
        session['draft'] = dfDraft.to_dict(orient='records')
        session['roster'] = dfRoster.to_dict(orient='records')
        session['total_picks'] = (roster_size - 2) * num_teams
        return render_template('draft.html', title='Draft', 
                                draft_head=draft_head,
                                repl_head=repl_head, 
                                team_head=team_head,
                                pick_label=pick_label, 
                                team_label=team_label,
                                next_pick_label=next_pick_label,
                                prev_pick_label=prev_pick_label,
                                prev_team_label=prev_team_label,
                                prev_player_label=prev_player_label,
                                prev_pos_label=prev_pos_label
                            )
    else:
        return redirect(url_for('settings'))


@app.route("/draft_data", methods=['GET', 'POST'])
def draft_data():  
    if request.method == 'POST' and 'player' in request.form: 
        session['pick_num'] += 1   
        pick_num = session['pick_num']
        lst_picks = session['lst_picks']
        team_picking = session['team_picking']
        player = request.form['player']
        position = request.form['position']
        fantasy_points = request.form['fantasy_points']
        dfRoster = pd.DataFrame.from_dict(session['roster'])
        dfPlayer = pd.DataFrame([[team_picking[pick_num - 2], lst_picks[pick_num - 2], player, position, fantasy_points]], columns=['team', 'pick', 'player', 'position', 'fantasy_points'])
        dfRoster = pd.concat([dfRoster, dfPlayer], ignore_index=True)          
        session['roster'] = dfRoster.to_dict(orient='records')
    elif request.method == 'POST' and 'player' not in request.form:
        session['pick_num'] -= 1
        dfRoster = pd.DataFrame.from_dict(session['roster'])
        dfRoster = dfRoster[:-1]         
        session['roster'] = dfRoster.to_dict(orient='records')        

    pick_num = session['pick_num']
    lst_picks_ov = session['lst_picks_ov']
    lst_picks = session['lst_picks']
    next_pick_in = session['next_pick_in']
    team_picking = session['team_picking']
    total_picks = session['total_picks']
    dfDraft = pd.DataFrame.from_dict(session['draft'])
    total_players = len(dfDraft)
    dfRoster = pd.DataFrame.from_dict(session['roster'])
    dfDraft = dfDraft.loc[~dfDraft['player'].isin(dfRoster['player'])]
    if dfDraft.empty:
        return jsonify({'draftdata': '',
                        'repldata': '',
                        'teamdata': '',
                        'pick_label': '',
                        'next_pick_label': '',
                        'team_label': '',
                        'prev_pick_label': '',
                        'prev_team_label': '',
                        'prev_player_label': '',
                        'prev_pos_label': '',
                        'pick_num': pick_num,
                        'total_picks': total_picks,
                        'total_players': total_players
                        })
    draftdata, repldata = ranking(dfDraft, pick_num, next_pick_in)
    dfTeam = pd.DataFrame.from_dict(session['roster'])
    dfTeam = dfTeam.loc[dfTeam.team == team_picking[pick_num - 1]]
    teamdata = dfTeam.to_dict(orient='records')    
    team_label = 'Team ' + str(team_picking[pick_num - 1])
    pick_label = 'Current Pick: ' + lst_picks[pick_num - 1] + ' - #' + str(pick_num) + ' Overall'
    next_pick_label = 'Next Pick: ' + lst_picks[pick_num + next_pick_in[pick_num - 1] - 1] + ' - #' + str(lst_picks_ov[pick_num + next_pick_in[pick_num - 1] - 1]) + ' Overall'  
    prev_pick_label = 'Latest Pick: ' + (lst_picks[pick_num - 2] if pick_num > 1 else '0.0')
    prev_team_label = 'Made By: Team ' + (str(team_picking[pick_num - 2]) if pick_num > 1 else '0')
    prev_player_label = str(dfRoster.iloc[-1].at['player']) if pick_num > 1 else 'Player'
    prev_pos_label = str(dfRoster.iloc[-1].at['position']) if pick_num > 1 else 'Position'
    return jsonify({'draftdata': draftdata,
                    'repldata': repldata,
                    'teamdata': teamdata,
                    'pick_label': pick_label,
                    'next_pick_label': next_pick_label,
                    'team_label': team_label,
                    'prev_pick_label': prev_pick_label,
                    'prev_team_label': prev_team_label,
                    'prev_player_label': prev_player_label,
                    'prev_pos_label': prev_pos_label,
                    'pick_num': pick_num,
                    'total_picks': total_picks,
                    'total_players': total_players
                    })


@app.route("/results", methods=['GET', 'POST'])
def results():
    if request.method == "POST":
        result_head = ['Team', 'Pick', 'Player', 'Pos', 'FPts']
        return render_template('results.html', title='Draft', result_head=result_head)
    else:
        return redirect(url_for('settings'))


@app.route("/results_data", methods=['GET'])
def results_data():
    resultsdata = session['roster'][1:]
    return jsonify({'data' : resultsdata})


@app.route("/settings/num_rounds/<system>")
def num_rounds(system):
    if system == 'Rookie':
        choices = [*range(3, 6)]
    elif system == 'Dynasty':    
        choices = [*range(20, 31)]
    else:
        choices = [*range(10, 17)]
    return jsonify({'num_rounds': choices})


@app.route("/settings/adp_sources/<system>/<scoring>")
def adp_sources(system, scoring):
    choices = sorted([src.source_name.replace('FantasyPros-', '') for src in Adp.query.with_entities(Adp.source_name).filter(Adp.season==2022, Adp.system==system, 
        Adp.scoring==scoring).distinct()], key=str.casefold)
    if system == '1-QB':
        choices = ['All (Average)'] + choices
    return jsonify({'adp_sources': choices})
