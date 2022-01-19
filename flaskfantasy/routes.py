from flask import render_template, url_for, request, redirect, session, jsonify, flash
from flaskfantasy import app, mail
from flaskfantasy.forms import SettingsForm, BeginForm, ContactForm
import pandas as pd
import psycopg2
from psycopg2.extensions import parse_dsn
import os
from flask_mail import Message

DATABASE_URL = parse_dsn(os.environ.get('DATABASE_URL'))

def priority(adp, pick_num, next_pick_in, num_teams):
    if adp <= pick_num + next_pick_in[pick_num - 1]:
        priority = {'display': 'High', 'priority': 1}
    elif adp >= pick_num + next_pick_in[pick_num - 1] + next_pick_in[pick_num + next_pick_in[pick_num - 1] - 1]:
        priority = {'display': 'Low', 'priority': 3}
    else:
        priority = {'display': 'Medium', 'priority': 2}
    return priority

def ranking(dfDraft, pick_num, next_pick_in, num_teams):
    dfTopPlayersNextRd = dfDraft.sort_values('adp')
    dfTopPlayersNextRd = dfTopPlayersNextRd.tail(len(dfTopPlayersNextRd) - next_pick_in[pick_num - 1])
    dfTopPlayersNextRd = dfTopPlayersNextRd.groupby('position').head(1)[['player', 'position', 'adp', 'fantasy_points']]
    dict_pos = dict(zip(dfTopPlayersNextRd['position'], dfTopPlayersNextRd['fantasy_points']))
    dfDraft['vor_pts'] = dfDraft.apply(lambda row: row['fantasy_points'] - (dict_pos.get(row['position'])), axis=1).round(1)
    dfDraft['vor_pct'] = dfDraft.apply(lambda row: (row['fantasy_points'] - dict_pos.get(row['position'])) / dict_pos.get(row['position']) * 100, axis=1).round(1)
    dfTopPlayersAvail = dfDraft.sort_values(by='vor_pct', ascending=False)[['player', 'position', 'adp', 'fantasy_points', 'vor_pts', 'vor_pct']]
    dfTopPlayersAvail['priority'] = dfTopPlayersAvail.apply(lambda x: priority(x['adp'], pick_num, next_pick_in, num_teams), axis=1)
    draftdata = dfTopPlayersAvail[['player', 'position', 'fantasy_points', 'vor_pts', 'vor_pct', 'adp', 'priority']].to_dict(orient='records')
    repldata = dfTopPlayersNextRd[['player', 'position', 'fantasy_points', 'adp']].to_dict(orient='records')   
    return draftdata, repldata    

@app.route("/", methods=['GET','POST'])
@app.route("/home", methods=['GET','POST'])
def home():
    form = BeginForm()
    if form.validate_on_submit():
        return redirect(url_for('settings'))
    return render_template('home.html', form=form)

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
    if form.validate_on_submit():
        return redirect(url_for('draft'))
    return render_template('settings.html', title='Settings', form=form)
    
@app.route("/draft", methods=['GET', 'POST'])
def draft():
    if request.method == 'POST':      
        session.clear()
        scoring_format = request.form['scoring_format']
        num_teams = int(request.form['num_teams'])
        roster_size = int(request.form['roster_size']) + 2 #Two extra round to have something to compare to in the last round
        projections_source = request.form['projections_source']
        adp_source = request.form['adp_source']
        pick_num = 1
        dfRoster = pd.DataFrame(data=[['', '', '', '', '']], columns=['team', 'pick', 'player', 'position', 'fantasy_points'])
    
        lst_picks_ov = []
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
        
        format_values = {'Half-PPR':[0.04, 4, -2, 0.1, 6, 0.5, 0.1, 6],
                         'PPR':[0.04, 4, -2, 0.1, 6, 1, 0.1, 6],
                         'Non-PPR':[0.04, 4, -2, 0.1, 6, 1, 0.1, 6]}
        
        con = psycopg2.connect(f"dbname={DATABASE_URL.get('dbname')} user={DATABASE_URL.get('user')} password={DATABASE_URL.get('password')} host={DATABASE_URL.get('host')} port={DATABASE_URL.get('port')}")
        cur = con.cursor()
        query = f"""
        
        SELECT A.player, A.position, A.fantasy_points, B.adp
        FROM        
            (SELECT player, position, passing_yard   * {format_values[scoring_format][0]}
                                                    + passing_td     * {format_values[scoring_format][1]}
                                                    + passing_int    * {format_values[scoring_format][2]}
                                                    + rushing_yard   * {format_values[scoring_format][3]}
                                                    + rushing_td     * {format_values[scoring_format][4]}
                                                    + receiving_rec  * {format_values[scoring_format][5]}
                                                    + receiving_yard * {format_values[scoring_format][6]}
                                                    + receiving_td   * {format_values[scoring_format][7]} AS fantasy_points
                        FROM projections
                        WHERE source_name = '{projections_source}'
                        AND source_update = (SELECT MAX(source_update) FROM projections WHERE source_name = '{projections_source}')
            ) A
            LEFT JOIN
            (SELECT player, position, adp
                        FROM average_draft_position
                        WHERE source_name = '{adp_source}'
                        AND scoring = '{scoring_format}'
                        AND source_update = (SELECT MAX(source_update) FROM average_draft_position WHERE source_name = '{adp_source}')
            ) B
            ON (A.player=B.player AND A.position=B.position)
            ORDER BY fantasy_points DESC        
            
                 """
        cur.execute(query)
        dfDraft = pd.DataFrame(cur.fetchall(), columns=['player', 'position', 'fantasy_points', 'adp'])
        cur.close()
        con.close()
        session['pick_num'] = pick_num
        session['lst_picks_ov'] = lst_picks_ov
        session['lst_picks'] = lst_picks
        session['next_pick_in'] = next_pick_in
        session['team_picking'] = team_picking
        session['roster_size'] = roster_size
        session['num_teams'] = num_teams       

        dfDraft['fantasy_points'] =  dfDraft['fantasy_points'].astype(float).round(1)
        dfDraft['adp'] =  dfDraft['adp'].astype(float).fillna(999)
        draftdata, repldata = ranking(dfDraft, pick_num, next_pick_in, session['num_teams'])
        Cols1 = ['', 'Player', 'Pos', 'FPts', 'Gap', 'Gap %', 'ADP', 'Priority']
        Cols2 = ['Player', 'Pos', 'FPts', 'ADP']
        Cols3 = ['Pos', 'Player']
        pick_label = 'Current Pick: ' + lst_picks[pick_num - 1] + ' - #' + str(pick_num) + ' Overall'
        team_label = 'Team ' + str(team_picking[pick_num - 1])
        next_pick_label = 'Next Pick: ' + lst_picks[pick_num + next_pick_in[pick_num - 1] - 1] + ' - #' + str(lst_picks_ov[pick_num + next_pick_in[pick_num - 1] - 1]) + ' Overall'
        prev_pick_label = 'Latest Pick: 0.0'
        prev_team_label = 'Made By: Team 0'
        prev_player_label = 'Player'
        prev_pos_label = 'Position'
        session['draft'] = draftdata   
        session['roster'] = dfRoster.to_dict(orient='records')
        session['total_picks'] = (roster_size - 2) * num_teams
        return render_template('draft.html', title='Draft', 
                                pick_label=pick_label, 
                                team_label=team_label,
                                next_pick_label=next_pick_label,
                                prev_pick_label=prev_pick_label,
                                prev_team_label=prev_team_label,
                                prev_player_label=prev_player_label,
                                prev_pos_label=prev_pos_label,
                                headings1=Cols1,
                                headings2=Cols2, 
                                headings3=Cols3)
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
    #return ''
    pick_num = session['pick_num']
    lst_picks_ov = session['lst_picks_ov']
    lst_picks = session['lst_picks']
    next_pick_in = session['next_pick_in']
    team_picking = session['team_picking']
    total_picks = session['total_picks']
    dfDraft = pd.DataFrame.from_dict(session['draft'])
    dfRoster = pd.DataFrame.from_dict(session['roster'])
    dfDraft = dfDraft.loc[~dfDraft['player'].isin(dfRoster['player'])]
    draftdata, repldata = ranking(dfDraft, pick_num, next_pick_in, session['num_teams'])
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
                    'pick_num': pick_num,
                    'total_picks': total_picks,
                    'prev_pick_label': prev_pick_label,
                    'prev_team_label': prev_team_label,
                    'prev_player_label': prev_player_label,
                    'prev_pos_label': prev_pos_label})

@app.route("/results", methods=['GET', 'POST'])
def results():
    if request.method == "POST":
        cols = ['Team', 'Pick', 'Player', 'Pos', 'FPts']
        return render_template('results.html', cols=cols)
    else:
        return redirect(url_for('settings'))
    
@app.route("/results_data", methods=['GET'])
def results_data():
    resultsdata = session['roster'][1:]
    return jsonify({'data' : resultsdata})