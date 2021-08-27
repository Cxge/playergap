from flask import render_template, url_for, request, redirect, flash, session
from flaskfantasy import app
from flaskfantasy.forms import SettingsForm, PlayerSelectionForm, BeginForm
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

@app.route("/draft", methods=['POST', 'GET'])
def draft():
    global player_list
    settings_form = SettingsForm()
    selection_form = PlayerSelectionForm()
    if settings_form.save_settings.data and request.method == 'POST':      
        session['scoring_format'] = request.form['scoring_format']
        session['num_teams'] = int(request.form['num_teams'])
        session['roster_size'] = int(request.form['roster_size'])
        session['projections_source'] = request.form['projections_source']
        session['adp_source'] = request.form['adp_source']
        session['pick_num'] = 1
        session['selected_players'] = ['Placeholder']
        
        next_pick = []
        next_round = []
        next_pick_in = []
        for i in range(session['roster_size'] + 1): #One extra round to have something to compare to
            for j in range(session['num_teams']):
                next_round.append(i + 1)
            next_pick += range(1, session['num_teams'] + 1)
            next_pick_in += reversed(range(1, session['num_teams'] * 2, 2))
        next_pick_in = [session['num_teams'] * 2 if n == 1 else n for n in next_pick_in]
        
        session['next_pick'] = next_pick
        session['next_pick_in'] = next_pick_in
        session['next_round'] = next_round
        
    elif selection_form.submit_selection.data and selection_form.validate_on_submit():
        selection = request.form['selection']
        selection_alt = selection.replace("'", "''")     
        if  selection_alt in session['selected_players']:
            flash(f'{selection} has already been selected. Please try again', 'warning')
            return redirect(url_for('draft'))
        elif selection not in player_list:
            flash(f'There is no player named "{selection}". Please try again', 'danger')
            return redirect(url_for('draft'))
        else:
            flash(f'{selection} has been selected', 'success')
            selection = selection.replace("'", "''") #Single quote escape for PostgreSQL query
            session['selected_players'].append(selection)
            session['pick_num'] += 1
            if session['pick_num'] == session['roster_size'] * session['num_teams']:
                flash('That was the last pick of the draft. Good luck!', 'success')
                return redirect(url_for('home'))
        return redirect(url_for('draft'))
        
    selected_players_array = ','.join(f"'{p}'" for p in session['selected_players']) 
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
    cur.close()
    con.close()
    dfDraft['fantasy_points'] =  dfDraft['fantasy_points'].astype(float).round(1)
    dfDraft['adp'] =  dfDraft['adp'].astype(float)
    player_list = sorted(dfDraft['player'].tolist())
       
    dfTopPlayersAvail = dfDraft.groupby('position').head(3)[['player', 'position', 'adp', 'fantasy_points']]
    dfTopPlayersNextRd = dfDraft.sort_values('adp')
    dfTopPlayersNextRd = dfTopPlayersNextRd.tail(len(dfTopPlayersNextRd) - session['next_pick_in'][session['pick_num'] - 1])
    dfTopPlayersNextRd = dfTopPlayersNextRd.groupby('position').head(1)[['player', 'position', 'adp', 'fantasy_points']]
    dict_pos = dict(zip(dfTopPlayersNextRd['position'], dfTopPlayersNextRd['fantasy_points']))
    dfTopPlayersAvail['vor_pts'] = dfTopPlayersAvail.apply(lambda row: row['fantasy_points'] - dict_pos.get(row['position']), axis=1).round(1)
    dfTopPlayersAvail['vor_pct'] = dfTopPlayersAvail.apply(lambda row: (row['fantasy_points'] - dict_pos.get(row['position'])) / dict_pos.get(row['position']) * 100, axis=1).round(1)
    dfTopPlayersAvail['rank'] = dfTopPlayersAvail['vor_pct'].rank(method='first', ascending=False)
    dfTopPlayersAvail['rank'] = dfTopPlayersAvail['rank'].astype(int)
    dfTopPlayersAvail = dfTopPlayersAvail.sort_values(by='rank', ascending=True)[['rank', 'player', 'position', 'adp', 'fantasy_points', 'vor_pts', 'vor_pct']]
    dfTopPlayersAvail['priority'] = np.where(dfTopPlayersAvail['adp'] >= session['pick_num'] + session['next_pick_in'][session['pick_num'] - 1], 'Low', 'High')
    
    dfTopPlayersAvailDict = dfTopPlayersAvail[['rank', 'player', 'position', 'fantasy_points', 'vor_pts', 'vor_pct', 'adp', 'priority']].to_dict(orient='records')
    Cols1 = ['', 'PLAYER', 'POS', 'FPTS', 'VOR', '%', 'ADP', 'URGENCY']
    dfTopPlayersNextRdDict = dfTopPlayersNextRd[['player', 'position', 'fantasy_points', 'adp']].to_dict(orient='records')
    Cols2 = ['PLAYER', 'POS', 'FPTS', 'ADP']
    
    pick_label = 'Pick: ' + str(session['next_round'][session['pick_num'] - 1]) + '.' + str(session['next_pick'][session['pick_num'] - 1])
    overall_pick_label = 'Overall: ' + str(session['pick_num'])
    next_pick_label = 'Next Pick: ' + str(session['next_round'][session['pick_num'] + session['next_pick_in'][session['pick_num'] - 1] - 1]) + '.' + str(session['next_pick'][session['pick_num'] + session['next_pick_in'][session['pick_num'] - 1] - 1])
    overall_next_pick_label = 'Overall: ' + str(session['pick_num'] + session['next_pick_in'][session['pick_num'] - 1])
    return render_template('draft.html', title='Draft', form=selection_form, 
                           pick_label=pick_label, 
                           overall_pick_label=overall_pick_label,
                           next_pick_label=next_pick_label,
                           overall_next_pick_label=overall_next_pick_label,
                           player_list=player_list,
                           headings1=Cols1, data1=dfTopPlayersAvailDict,
                           headings2=Cols2, data2=dfTopPlayersNextRdDict)


