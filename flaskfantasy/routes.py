from flask import render_template, url_for, request, redirect, flash
from flaskfantasy import app
from flaskfantasy.forms import SettingsForm, PlayerSelectionForm, BeginForm
import pandas as pd
import numpy as np
import psycopg2
import os

DATABASE_URL = os.environ.get('DATABASE_URL')

@app.route("/", methods=['GET','POST'])
@app.route("/home", methods=['GET','POST'])
def home():
    form = BeginForm()
    if form.validate_on_submit():
        return redirect(url_for('settings'))
    return render_template('home.html', form=form)

@app.route("/settings", methods=['GET', 'POST'])
def settings():
    global pick_num, dfTopPlayersAvail, dfTopPlayersNextRd, dfDraft, next_pick_in, next_pick, next_round
    form = SettingsForm()
    if form.validate_on_submit():
        scoring_format = request.form['scoring_format']
        num_teams = int(request.form['num_teams'])
        projections_source = request.form['projections_source']
        adp_source = request.form['adp_source']
        pick_num = 1
        format_values = {'Half-PPR':[0.04, 4, -2, 0.1, 6, 0.5, 0.1, 6],
                         'PPR':[0.04, 4, -2, 0.1, 6, 1, 0.1, 6],
                         'Non-PPR':[0.04, 4, -2, 0.1, 6, 1, 0.1, 6]}
        con = psycopg2.connect(DATABASE_URL, sslmode='require')
        cur = con.cursor()
        proj_query = f"""SELECT player, position, passing_yard   * {format_values[scoring_format][0]}
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
                    ORDER BY position, fantasy_points DESC
                 """
        adp_query = f"""SELECT player, position, adp
                        FROM average_draft_position
                        WHERE source_name = '{adp_source}'
                        AND scoring = '{scoring_format}'
                        AND source_update = (SELECT MAX(source_update) FROM average_draft_position WHERE source_name = '{adp_source}')
                        ORDER BY adp
                     """
        cur.execute(proj_query)
        dfProjections = pd.DataFrame(cur.fetchall(), columns=['player', 'position', 'fantasy_points'])
        dfProjections['fantasy_points'] =  dfProjections['fantasy_points'].astype(float)
        cur.execute(adp_query)
        dfADP = pd.DataFrame(cur.fetchall(), columns=['player', 'position', 'adp'])
        dfADP['adp'] =  dfADP['adp'].astype(float)
        cur.close()
        con.close()

        dfDraft = dfProjections.merge(dfADP, how='left', on=['player', 'position'])
        dfDraft['status'] = 'Available'
        # dfDraft['fantasy_points'] =   dfDraft['passing_yard'] / 25 \
        #                             + dfDraft['passing_td'] * 4 \
        #                             + dfDraft['passing_int'] * -2 \
        #                             + dfDraft['rushing_yard'] / 10 \
        #                             + dfDraft['rushing_td'] * 6 \
        #                             + dfDraft['receiving_rec'] * 0.5 \
        #                             + dfDraft['receiving_yard'] / 10 \
        #                             + dfDraft['receiving_td'] * 6
        #dfDraft['fantasy_points'] = dfDraft['fantasy_points'].round(1)
        dfDraft = dfDraft.sort_values('fantasy_points', ascending=False)
        num_rounds = 15
        num_teams = 12
        next_pick = []
        next_round = []
        next_pick_in = []
        for i in range(num_rounds):
            for j in range(num_teams):
                next_round.append(i + 1)
            next_pick += range(1, num_teams + 1)
            next_pick_in += reversed(range(1, num_teams * 2, 2))
        next_pick_in = [num_teams * 2 if n == 1 else n for n in next_pick_in]
        
        dfPlayersAvail = dfDraft.loc[dfDraft['status'] == 'Available']
        dfTopPlayersAvail = dfPlayersAvail.groupby('position').head(3)[['player', 'position', 'adp', 'fantasy_points']]
        dfTopPlayersNextRd = dfPlayersAvail.sort_values('adp')
        dfTopPlayersNextRd = dfTopPlayersNextRd.tail(len(dfTopPlayersNextRd) - next_pick_in[pick_num - 1])
        dfTopPlayersNextRd = dfTopPlayersNextRd.groupby('position').head(1)[['player', 'position', 'adp', 'fantasy_points']]
        dict_pos = dict(zip(dfTopPlayersNextRd['position'], dfTopPlayersNextRd['fantasy_points']))
        dfTopPlayersAvail['vor_pts'] = dfTopPlayersAvail.apply(lambda row: row['fantasy_points'] - dict_pos.get(row['position']), axis=1).round(1)
        dfTopPlayersAvail['vor_pct'] = dfTopPlayersAvail.apply(lambda row: (row['fantasy_points'] - dict_pos.get(row['position'])) / dict_pos.get(row['position']) * 100, axis=1).round(1)
        dfTopPlayersAvail['rank'] = dfTopPlayersAvail['vor_pct'].rank(method='first', ascending=False)
        dfTopPlayersAvail['rank'] = dfTopPlayersAvail['rank'].astype(int)
        dfTopPlayersAvail = dfTopPlayersAvail.sort_values(by='rank', ascending=True)[['rank', 'player', 'position', 'adp', 'fantasy_points', 'vor_pts', 'vor_pct']]
        dfTopPlayersAvail['priority'] = np.where(dfTopPlayersAvail['adp'] >= pick_num + next_pick_in[pick_num - 1], 'Low', 'High')
        #END QUERY
        
        return redirect(url_for('draft'))
    return render_template('settings.html', title='Settings', form=form)      

@app.route("/draft", methods=['GET','POST'])
def draft():
    global pick_num, dfTopPlayersAvail, dfTopPlayersNextRd, dfDraft, next_pick_in
    selection_form = PlayerSelectionForm()
    player_list = sorted(dfDraft['player'].tolist())
    if selection_form.submit_selection.data and selection_form.validate_on_submit():
        #selection = request.form['selection']
        selection = selection_form.selection.data
        if selection not in player_list:
            flash(f'There is no player named "{selection}". Please try again', 'danger')
            return redirect(url_for('draft'))
        elif dfDraft.loc[dfDraft['player'] == selection, 'status'].item() == 'Picked':
            flash(f'{selection} has already been selected. Please try again', 'warning')
            return redirect(url_for('draft'))
        else:
            flash(f'{selection} has been selected', 'success')
            pick_num += 1
            dfDraft.loc[dfDraft['player'] == selection, 'status'] = 'Picked'
            dfPlayersAvail = dfDraft.loc[dfDraft['status'] == 'Available']
            dfTopPlayersAvail = dfPlayersAvail.groupby('position').head(3)[['player', 'position', 'adp', 'fantasy_points']]
            dfTopPlayersNextRd = dfPlayersAvail.sort_values('adp')
            dfTopPlayersNextRd = dfTopPlayersNextRd.tail(len(dfTopPlayersNextRd) - next_pick_in[pick_num - 1])
            dfTopPlayersNextRd = dfTopPlayersNextRd.groupby('position').head(1)[['player', 'position', 'adp', 'fantasy_points']]
            dict_pos = dict(zip(dfTopPlayersNextRd['position'], dfTopPlayersNextRd['fantasy_points']))
            dfTopPlayersAvail['vor_pts'] = dfTopPlayersAvail.apply(lambda row: row['fantasy_points'] - dict_pos.get(row['position']), axis=1).round(1)
            dfTopPlayersAvail['vor_pct'] = dfTopPlayersAvail.apply(lambda row: (row['fantasy_points'] - dict_pos.get(row['position'])) / dict_pos.get(row['position']) * 100, axis=1).round(1)
            dfTopPlayersAvail['rank'] = dfTopPlayersAvail['vor_pct'].rank(method='first', ascending=False)
            dfTopPlayersAvail['rank'] = dfTopPlayersAvail['rank'].astype(int)
            dfTopPlayersAvail = dfTopPlayersAvail.sort_values(by='rank', ascending=True)[['rank', 'player', 'position', 'adp', 'fantasy_points', 'vor_pts', 'vor_pct' ]]
            dfTopPlayersAvail['priority'] = np.where(dfTopPlayersAvail['adp'] >= pick_num + next_pick_in[pick_num - 1], 'Low', 'High')
            return redirect(url_for('draft'))
    
    dfTopPlayersAvailDict = dfTopPlayersAvail[['rank', 'player', 'position', 'fantasy_points', 'vor_pts', 'vor_pct', 'adp', 'priority']].to_dict(orient='records')
    Cols1 = ['', 'PLAYER', 'POS', 'FPTS', 'VOR', '%', 'ADP', 'URGENCY']
    dfTopPlayersNextRdDict = dfTopPlayersNextRd[['player', 'position', 'fantasy_points', 'adp']].to_dict(orient='records')
    Cols2 = ['PLAYER', 'POS', 'FPTS', 'ADP']
    
    pick_label = 'Pick: ' + str(next_round[pick_num - 1]) + '.' + str(next_pick[pick_num - 1])
    overall_pick_label = 'Overall: ' + str(pick_num)
    next_pick_label = 'Next Pick: ' + str(next_round[pick_num + next_pick_in[pick_num - 1] - 1]) + '.' + str(next_pick[pick_num + next_pick_in[pick_num - 1] - 1])
    overall_next_pick_label = 'Overall: ' + str(pick_num + next_pick_in[pick_num - 1])
    return render_template('draft.html', title='Draft', form=selection_form, 
                           pick_label=pick_label, 
                           overall_pick_label=overall_pick_label,
                           next_pick_label=next_pick_label,
                           overall_next_pick_label=overall_next_pick_label,
                           player_list=player_list,
                           headings1=Cols1, data1=dfTopPlayersAvailDict,
                           headings2=Cols2, data2=dfTopPlayersNextRdDict)


