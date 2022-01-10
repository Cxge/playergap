from flask import render_template, url_for, request, redirect, session, jsonify, flash
from flaskfantasy import app, mail
from flaskfantasy.forms import SettingsForm, BeginForm, ContactForm
import pandas as pd
import numpy as np
import psycopg2
from psycopg2.extensions import parse_dsn
import os
from flask_mail import Message

DATABASE_URL = parse_dsn(os.environ.get('DATABASE_URL'))

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
        dfRoster = pd.DataFrame(data=[['', '', '', '', '', '']], columns=['team', 'overall', 'pick', 'player', 'position', 'fantasy_points'])
    
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
        
        dfTopPlayersNextRd = dfDraft.sort_values('adp')
        dfTopPlayersNextRd = dfTopPlayersNextRd.tail(len(dfTopPlayersNextRd) - next_pick_in[pick_num - 1])
        #AGREGAR QB DE A MENTIS CON CERO PUNTOS?
        dfTopPlayersNextRd = dfTopPlayersNextRd.groupby('position').head(1)[['player', 'position', 'adp', 'fantasy_points']]
        dict_pos = dict(zip(dfTopPlayersNextRd['position'], dfTopPlayersNextRd['fantasy_points']))
        dfDraft['vor_pts'] = dfDraft.apply(lambda row: row['fantasy_points'] - (dict_pos.get(row['position'])), axis=1).round(1)
        dfDraft['vor_pct'] = dfDraft.apply(lambda row: (row['fantasy_points'] - dict_pos.get(row['position'])) / dict_pos.get(row['position']) * 100, axis=1).round(1)
        dfDraft['rank'] = dfDraft['vor_pct'].rank(method='first', ascending=False)
        dfDraft['rank'] = dfDraft['rank'].astype(int)
        dfTopPlayersAvail = dfDraft.sort_values(by='rank', ascending=True)[['rank', 'player', 'position', 'adp', 'fantasy_points', 'vor_pts', 'vor_pct']]
        dfTopPlayersAvail['urgency'] = np.where(dfTopPlayersAvail['adp'] >= pick_num + next_pick_in[pick_num - 1], 'Low', 'High')
        dfTopPlayersAvailDict = dfTopPlayersAvail[['rank', 'player', 'position', 'fantasy_points', 'vor_pts', 'vor_pct', 'adp', 'urgency']].to_dict(orient='records')
        Cols1 = ['', 'Rk', 'Player', 'Pos', 'FPts', 'Gap', '%', 'ADP', 'Urgency']
        dfTopPlayersNextRdDict = dfTopPlayersNextRd[['player', 'position', 'fantasy_points', 'adp']].to_dict(orient='records')
        Cols2 = ['Player', 'Pos', 'FPts', 'ADP']
        Cols3 = ['Pos', 'Player']
        
        pick_label = 'Current Pick: ' + lst_picks[pick_num - 1] + ' - #' + str(pick_num) + ' Overall'
        next_pick_label = 'Next Pick: ' + lst_picks[pick_num + next_pick_in[pick_num - 1] - 1] + ' - #' + str(lst_picks_ov[pick_num + next_pick_in[pick_num - 1] - 1]) + ' Overall'
        team_label = 'Team ' + str(team_picking[pick_num - 1])
        session['draft'] = dfTopPlayersAvailDict
        session['replacements'] = dfTopPlayersNextRdDict    
        session['roster'] = dfRoster.to_dict(orient='records')
        session['total_picks'] = (roster_size - 2) * num_teams
        return render_template('draft.html', title='Draft', 
                                pick_label=pick_label, 
                                next_pick_label=next_pick_label,
                                headings1=Cols1,
                                headings2=Cols2, 
                                team_label=team_label,
                                headings3=Cols3)
    else:
        return redirect(url_for('settings'))

@app.route("/draft_data", methods=['GET', 'POST'])
def draft_data():
    if request.method == "POST":
        session['pick_num'] += 1
        pick_num = session['pick_num']
        lst_picks_ov = session['lst_picks_ov']
        lst_picks = session['lst_picks']
        next_pick_in = session['next_pick_in']
        team_picking = session['team_picking']
        total_picks = session['total_picks']
        
        player = request.form['player']
        position = request.form['position']
        fantasy_points = request.form['fantasy_points']
        dfDraft = pd.DataFrame.from_dict(session['draft'])
        dfDraft.drop(dfDraft[dfDraft['player'] == player].index, inplace=True)
        
        dfTopPlayersNextRd = dfDraft.sort_values('adp')
        dfTopPlayersNextRd = dfTopPlayersNextRd.tail(len(dfTopPlayersNextRd) - next_pick_in[pick_num - 1])
        
        dfTopPlayersNextRd = dfTopPlayersNextRd.groupby('position').head(1)[['player', 'position', 'adp', 'fantasy_points']]
        dict_pos = dict(zip(dfTopPlayersNextRd['position'], dfTopPlayersNextRd['fantasy_points']))
        dfDraft['vor_pts'] = dfDraft.apply(lambda row: row['fantasy_points'] - (dict_pos.get(row['position'])), axis=1).round(1)
        dfDraft['vor_pct'] = dfDraft.apply(lambda row: (row['fantasy_points'] - dict_pos.get(row['position'])) / dict_pos.get(row['position']) * 100, axis=1).round(1)
        dfDraft['rank'] = dfDraft['vor_pct'].rank(method='first', ascending=False)
        dfDraft['rank'] = dfDraft['rank'].astype(int)
        dfTopPlayersAvail = dfDraft.sort_values(by='rank', ascending=True)[['rank', 'player', 'position', 'adp', 'fantasy_points', 'vor_pts', 'vor_pct']]
        dfTopPlayersAvail['urgency'] = np.where(dfTopPlayersAvail['adp'] >= pick_num + next_pick_in[pick_num - 1], 'Low', 'High')
        dfTopPlayersAvailDict = dfTopPlayersAvail[['rank', 'player', 'position', 'fantasy_points', 'vor_pts', 'vor_pct', 'adp', 'urgency']].to_dict(orient='records')
        dfTopPlayersNextRdDict = dfTopPlayersNextRd[['player', 'position', 'fantasy_points', 'adp']].to_dict(orient='records')
        session['draft'] = dfTopPlayersAvailDict
        session['replacements'] = dfTopPlayersNextRdDict        
        dfRoster = pd.DataFrame.from_dict(session['roster'])
        dfPlayer = pd.DataFrame([[team_picking[pick_num - 2], pick_num - 1, lst_picks[pick_num - 2], player, position, fantasy_points]], columns=['team', 'overall', 'pick', 'player', 'position', 'fantasy_points'])
        dfRoster = pd.concat([dfRoster, dfPlayer], ignore_index=True)
        session['roster'] = dfRoster.to_dict(orient='records')
        draftdata = session['draft']
        team_label = 'Team ' + str(team_picking[pick_num - 1])
        pick_label = 'Current Pick: ' + lst_picks[pick_num - 1] + ' - #' + str(pick_num) + ' Overall'
        next_pick_label = 'Next Pick: ' + lst_picks[pick_num + next_pick_in[pick_num - 1] - 1] + ' - #' + str(lst_picks_ov[pick_num + next_pick_in[pick_num - 1] - 1]) + ' Overall'  
        return jsonify({'data': draftdata, 'pick_label': pick_label, 'next_pick_label': next_pick_label, 'team_label': team_label, 'pick_num': pick_num, 'total_picks': total_picks})
    else:
        data = session['draft']
        return jsonify({'data': data})
    
@app.route("/repl_data", methods=['GET'])
def repl_data():
    repldata = session['replacements']
    return jsonify({'data' : repldata})

@app.route("/team_data", methods=['GET'])
def team_data():
    pick_num = session['pick_num']
    team_picking = session['team_picking']
    dfTeam = pd.DataFrame.from_dict(session['roster'])
    dfTeam = dfTeam.loc[dfTeam.team == team_picking[pick_num - 1]]
    teamdata = dfTeam.to_dict(orient='records')
    return jsonify({'data' : teamdata})

@app.route("/results", methods=['GET', 'POST'])
def results():
    if request.method == "POST":
        cols = ['Team', 'Pick', 'Overall', 'Player', 'Position', 'Fantasy Pts']
        return render_template('results.html', cols=cols)
    else:
        return redirect(url_for('settings'))
    
@app.route("/results_data", methods=['GET'])
def results_data():
    resultsdata = session['roster'][1:]
    return jsonify({'data' : resultsdata})




