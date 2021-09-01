from flask import render_template, url_for, request, redirect, flash, session
from flaskfantasy import app
from flaskfantasy.forms import SettingsForm, BeginForm
import pandas as pd
import numpy as np
import psycopg2
from psycopg2.extensions import parse_dsn
import os

DATABASE_URL = parse_dsn(os.environ.get('DATABASE_URL'))

@app.route("/", methods=['GET','POST'])
@app.route("/home", methods=['GET','POST'])
def home():
    form = BeginForm()
    if form.validate_on_submit():
        return redirect(url_for('settings'))
    return render_template('home.html', form=form)

@app.route("/settings", methods=['GET', 'POST'])
def settings():
    form = SettingsForm()
    if form.validate_on_submit():
        return redirect(url_for('draft'))
    return render_template('settings.html', title='Settings', form=form)

@app.route("/select/<string:player>")
def select_player(player):
    session['pick_num'] += 1
    if session['pick_num'] == (session['roster_size'] - 1) * session['num_teams']:
        flash('That was the last pick of the draft. Good luck!', 'success')
        return redirect(url_for('home'))
    else:
        player = player.replace("'", "''") #Single quote escape for PostgreSQL query
        session['selected_players'].append(player)
        return redirect(url_for('draft'))

@app.route("/draft", methods=['GET', 'POST'])
def draft():
    settings_form = SettingsForm()
    if settings_form.save_settings.data and request.method == 'POST':      
        session.clear()
        session['scoring_format'] = request.form['scoring_format']
        session['num_teams'] = int(request.form['num_teams'])
        session['roster_size'] = int(request.form['roster_size']) + 1 #One extra round to have something to compare to in the last one
        session['projections_source'] = request.form['projections_source']
        session['adp_source'] = request.form['adp_source']
        session['pick_num'] = 1
        session['selected_players'] = ['Placeholder']    
    
    lst_picks_ov = []
    lst_picks_ov = [*range(1, session['roster_size'] * session['num_teams'] + 1)]
    
    lst_picks = []
    next_pick_in = []    
    for i in range(1, session['roster_size'] + 1):
        for j in range(1, session['num_teams'] + 1):
            lst_picks.append(str(i) + '.' + str(j))
        next_pick_in += reversed(range(1, session['num_teams'] * 2, 2))
    next_pick_in = [session['num_teams'] * 2 if n == 1 else n for n in next_pick_in]
        
    team_picking = []
    for j in range(1, session['roster_size'] + 1):
        if j % 2 == 0:
            team_picking += reversed(range(1, session['num_teams'] + 1))
        else:
            team_picking += range(1, session['num_teams'] + 1)
    
    team_picks = []
    for i in range(1, session['roster_size'] + 1):
        if i % 2 == 0:
            team_picks.append(i * session['num_teams'] - team_picking[session['pick_num'] - 1] + 1)
        else:
            team_picks.append((i - 1) * session['num_teams'] + team_picking[session['pick_num'] - 1])
            
    team_roster = ['Placeholder']     
    if session['pick_num'] > session['num_teams']:
        team_roster = [session['selected_players'][i] for i in team_picks[:((session['pick_num'] - 1) // session['num_teams'])]]

    selected_players_array = ','.join(f"'{p}'" for p in session['selected_players']) 
    team_roster_array = ','.join(f"'{p}'" for p in team_roster)
    
    format_values = {'Half-PPR':[0.04, 4, -2, 0.1, 6, 0.5, 0.1, 6],
                     'PPR':[0.04, 4, -2, 0.1, 6, 1, 0.1, 6],
                     'Non-PPR':[0.04, 4, -2, 0.1, 6, 1, 0.1, 6]}
    
    con = psycopg2.connect(f"dbname={DATABASE_URL.get('dbname')} user={DATABASE_URL.get('user')} password={DATABASE_URL.get('password')} host={DATABASE_URL.get('host')} port={DATABASE_URL.get('port')}")
    cur = con.cursor()
    query = f"""
    
    SELECT A.player, A.position, A.fantasy_points, B.adp
    FROM        
        (SELECT player, position, passing_yard   * {format_values[session['scoring_format']][0]}
                                                + passing_td     * {format_values[session['scoring_format']][1]}
                                                + passing_int    * {format_values[session['scoring_format']][2]}
                                                + rushing_yard   * {format_values[session['scoring_format']][3]}
                                                + rushing_td     * {format_values[session['scoring_format']][4]}
                                                + receiving_rec  * {format_values[session['scoring_format']][5]}
                                                + receiving_yard * {format_values[session['scoring_format']][6]}
                                                + receiving_td   * {format_values[session['scoring_format']][7]} AS fantasy_points
                    FROM projections
                    WHERE source_name = '{session['projections_source']}'
                    AND source_update = (SELECT MAX(source_update) FROM projections WHERE source_name = '{session['projections_source']}')
        ) A
        LEFT JOIN
        (SELECT player, position, adp
                    FROM average_draft_position
                    WHERE source_name = '{session['adp_source']}'
                    AND scoring = '{session['scoring_format']}'
                    AND source_update = (SELECT MAX(source_update) FROM average_draft_position WHERE source_name = '{session['adp_source']}')
        ) B
        ON (A.player=B.player AND A.position=B.position)
        WHERE A.player NOT IN ({selected_players_array})
        ORDER BY fantasy_points DESC        
        
             """
    
    cur.execute(query)
    
    dfDraft = pd.DataFrame(cur.fetchall(), columns=['player', 'position', 'fantasy_points', 'adp'])
    
    query = f""" 
    SELECT position, player
    FROM projections
    WHERE source_name = '{session['projections_source']}'
    AND source_update = (SELECT MAX(source_update) FROM projections WHERE source_name = '{session['projections_source']}')
    AND player IN ({team_roster_array})
    ORDER BY position
    
            """
    cur.execute(query)
    
    dfRoster = pd.DataFrame(cur.fetchall(), columns=['position', 'player'])        
    
    cur.close()
    con.close()
    dfDraft['fantasy_points'] =  dfDraft['fantasy_points'].astype(float).round(1)
    dfDraft['adp'] =  dfDraft['adp'].astype(float).fillna(999)
    player_list = dfDraft.sort_values('adp')['player'].tolist()
    
    dfTopPlayersNextRd = dfDraft.sort_values('adp')
    dfTopPlayersNextRd = dfTopPlayersNextRd.tail(len(dfTopPlayersNextRd) - next_pick_in[session['pick_num'] - 1])
    #AGREGAR QB DE A MENTIS CON CERO PUNTOS?
    dfTopPlayersNextRd = dfTopPlayersNextRd.groupby('position').head(1)[['player', 'position', 'adp', 'fantasy_points']]
    dict_pos = dict(zip(dfTopPlayersNextRd['position'], dfTopPlayersNextRd['fantasy_points']))
    dfDraft['vor_pts'] = dfDraft.apply(lambda row: row['fantasy_points'] - (dict_pos.get(row['position'])), axis=1).round(1)
    dfDraft['vor_pct'] = dfDraft.apply(lambda row: (row['fantasy_points'] - dict_pos.get(row['position'])) / dict_pos.get(row['position']) * 100, axis=1).round(1)
    dfDraft['rank'] = dfDraft['vor_pct'].rank(method='first', ascending=False)
    dfDraft['rank'] = dfDraft['rank'].astype(int)
    dfTopPlayersAvail = dfDraft.sort_values(by='rank', ascending=True)[['rank', 'player', 'position', 'adp', 'fantasy_points', 'vor_pts', 'vor_pct']]
    dfTopPlayersAvail['priority'] = np.where(dfTopPlayersAvail['adp'] >= session['pick_num'] + next_pick_in[session['pick_num'] - 1], 'Low', 'High')
    
    dfTopPlayersAvailDict = dfTopPlayersAvail[['rank', 'player', 'position', 'fantasy_points', 'vor_pts', 'vor_pct', 'adp', 'priority']].to_dict(orient='records')
    Cols1 = ['', 'Rk', 'Player', 'Pos', 'FPts', 'Gap', '%', 'ADP', 'Urgency']
    dfTopPlayersNextRdDict = dfTopPlayersNextRd[['player', 'position', 'fantasy_points', 'adp']].to_dict(orient='records')
    Cols2 = ['Player', 'Pos', 'FPts', 'ADP']
    dfRoster = dfRoster.to_dict(orient='records')
    Cols3 = ['Pos', 'Player']
       
    pick_label = 'Current Pick: ' + lst_picks[session['pick_num'] - 1]
    overall_pick_label = '#' + str(session['pick_num']) + ' Overall'
    next_pick_label = 'Next Pick: ' + lst_picks[session['pick_num'] + next_pick_in[session['pick_num'] - 1] - 1]
    overall_next_pick_label = '#' + str(lst_picks_ov[session['pick_num'] + next_pick_in[session['pick_num'] - 1] - 1]) + ' Overall'
    team_picking_label = str(team_picking[session['pick_num'] - 1])
    return render_template('draft.html', title='Draft', 
                            pick_label=pick_label, 
                            overall_pick_label=overall_pick_label,
                            next_pick_label=next_pick_label,
                            overall_next_pick_label=overall_next_pick_label,
                            player_list=player_list,
                            headings1=Cols1, data1=dfTopPlayersAvailDict,
                            headings2=Cols2, data2=dfTopPlayersNextRdDict,
                            selected_players = session['selected_players'][1:],
                            team_picking_label=team_picking_label,
                            headings3=Cols3, data3=dfRoster)



