import pandas as pd
import numpy as np
from json import loads
from copy import deepcopy
from flask import render_template, url_for, request, redirect, session, jsonify, flash
from flask_mail import Message
from sqlalchemy import text

from flaskfantasy import app, db, mail
from flaskfantasy.forms import SettingsForm, ContactForm
from flaskfantasy.models import Adp


class DraftState:
    def __init__(self, free_agents, system, num_teams, roster_size):
        self.counter = 0
        
        self.picks = []
        self.picks_until_next = []    
        for i in range(1, (roster_size + 2) + 1):
            for j in range(1, num_teams + 1):
                self.picks.append(str(i) + '.' + str(j))
            self.picks_until_next += reversed(range(1, num_teams * 2, 2))
        self.picks_until_next = [num_teams * 2 if n == 1 else n for n in self.picks_until_next]
        
        self.team_picks = []
        for j in range(1, (roster_size + 2) + 1):
            if j % 2 == 0:
                self.team_picks += reversed(range(1, num_teams + 1))
            else:
                self.team_picks += range(1, num_teams + 1)
        
        self.picks_ov = [*range(1, num_teams * (roster_size + 2) + 1)]
        self.next_picks_ov = np.array(self.picks_ov) + np.array(self.picks_until_next)
        self.next_picks = [self.picks[i - 1] for i in self.next_picks_ov[:-2 * num_teams + 1]]
        self.rosters = [[] for _ in range(num_teams)] #Empty rosters to start with
        self.free_agents = free_agents
        self.total_players = len(free_agents)
        self.pick = self.picks[self.counter]
        self.pick_ov = self.picks_ov[self.counter]
        self.next_pick_ov =  self.next_picks_ov[self.counter]
        self.next_pick =  self.next_picks[self.counter]
        self.team_pick = self.team_picks[self.counter]
        self.system = system
        self.teams = [*range(1, num_teams + 1)]
        self.rounds = [*range(1, roster_size + 1)]
        self.picks_per_team = {}
        for j in range(1, num_teams + 1):
            self.picks_per_team[j] = [i for i, x in enumerate(self.team_picks) if x == j]
        
    def make_selection(self, player_name):
        player = next(p for p in self.free_agents if p.player == player_name)
        player.pick = self.pick
        player.team = self.team_pick
        self.counter += 1
        self.free_agents.remove(player)
        self.rosters[self.team_pick - 1].append(player)
        self.pick = self.picks[self.counter]
        self.pick_ov = self.picks_ov[self.counter]
        self.next_pick_ov =  self.next_picks_ov[self.counter]
        self.next_pick =  self.next_picks[self.counter]
        self.team_pick = self.team_picks[self.counter]

    def undo_selection(self):
        self.counter -= 1
        self.team_pick = self.team_picks[self.counter]
        player = self.rosters[self.team_pick - 1][-1]
        player.pick = None
        player.team = None
        self.free_agents.append(player)
        self.free_agents.sort(key=lambda x: (x.adp, -x.fantasy_points))
        self.rosters[self.team_pick - 1].remove(player)
        self.pick = self.picks[self.counter]
        self.pick_ov = self.picks_ov[self.counter]
        self.next_pick_ov =  self.next_picks_ov[self.counter]
        self.next_pick =  self.next_picks[self.counter]

    def make_projection(self, player_name):
        player = next(p for p in self.free_agents if p.player == player_name)
        self.counter += 1
        self.free_agents.remove(player)
        self.rosters[self.team_pick - 1].append(player)
        self.team_pick = self.team_picks[self.counter]

    def get_replacements(self, positions):
        if self.system == '1-QB':
            pos_weights = {
                'QB': [1],
                'WR': [1, 1, 1, 1],
                'RB': [1, 1, 1, 1],
                'TE': [1],
                'K': [1],
                'DST': [1]
            }
        else:
            pos_weights = {
                'QB': [1, 1],
                'WR': [1, 1, 1, 1],
                'RB': [1, 1, 1, 1],
                'TE': [1],
                'K': [1],
                'DST': [1]
            }

        for tm in self.team_picks[self.counter:next((i for i,n in enumerate(self.picks_ov) if n >= self.next_pick_ov))]:
            roster = self.rosters[tm - 1]
            moves = []
            for pos in positions:
                pos_num = sum(1 for pl in roster if pl.position == pos)
                pos_wgt = pos_weights[pos][pos_num] if len(pos_weights[pos]) > pos_num else 0.8
                move = next((m for m in deepcopy(self).free_agents if m.position == pos), NflPlayer('N/A', pos, 999.9, 0))
                move.adp /= pos_wgt
                moves.append(move)
            pick = min(moves, key=lambda x: x.adp)
            self.make_projection(pick.player)
        replacements = []
        for pos in positions:
            replacement = next((r for r in self.free_agents if r.position == pos), NflPlayer('N/A', pos, 999.9, 0))
            replacements.append(replacement) 
        return replacements

    def assign_keepers(self, keepers):
        remove_indices = []
        for k in keepers:
            player_name = k['player']
            position = k['position']
            tm = int(k['team'])
            rd = int(k['round'])
            player = next(p for p in self.free_agents if p.player == player_name and p.position == position)
            pick_index = self.picks_per_team[tm][rd-1]
            player.pick = self.picks[pick_index]
            player.team = tm
            self.free_agents.remove(player)
            self.rosters[tm - 1].append(player)
            remove_indices.append(pick_index)

        self.picks = [i for j, i in enumerate(self.picks) if j not in remove_indices]
        self.picks_ov = [i for j, i in enumerate(self.picks_ov) if j not in remove_indices]
        self.next_picks_ov = [i for j, i in enumerate(self.next_picks_ov) if j not in remove_indices]
        self.team_picks = [i for j, i in enumerate(self.team_picks) if j not in remove_indices]
        self.next_picks = [i for j, i in enumerate(self.next_picks) if j not in remove_indices]

        self.pick = self.picks[self.counter]
        self.pick_ov = self.picks_ov[self.counter]
        self.next_pick_ov =  self.next_picks_ov[self.counter]
        self.next_pick =  self.next_picks[self.counter]
        self.team_pick = self.team_picks[self.counter]
        self.pick_label = 'Current Pick: ' + str(self.pick) + ' - #' + str(self.pick_ov) + ' Overall'
        self.team_label = 'Team ' + str(self.team_pick)
        self.next_pick_label = 'Next Pick: ' + str(self.next_pick) + ' - #' + str(self.next_pick_ov) + ' Overall' 


class NflPlayer:
    def __init__(self, player, position, adp, fantasy_points, gap_pts=None, urgency=None, pick=None, team=None, rank=None):
        self.player = player
        self.position = position
        self.adp = adp
        self.fantasy_points = fantasy_points
        self.gap_pts = gap_pts
        self.urgency = urgency
        self.rank = rank
        
    def __repr__(self):
        return "|".join([self.player, self.position])

    def __eq__(self, other):
        if (isinstance(other, NflPlayer)):
            return self.player == other.player and self.position == other.position and self.adp == other.adp and self.fantasy_points == other.fantasy_points \
            and self.gap_pts == other.gap_pts and self.urgency == other.urgency
        return False

    def calc_urgency_adp(self, counter, picks_until_next, free_agents):
        if self in free_agents[:picks_until_next[counter]]:
            self.urgency = {'urgency': 1, 'display': 'High'}
        elif self in free_agents[picks_until_next[counter]:picks_until_next[counter] + picks_until_next[counter + picks_until_next[counter]]]:
            self.urgency = {'urgency': 2, 'display': 'Medium'}
        else:
            self.urgency = {'urgency': 3, 'display': 'Low'}
        return self

    def calc_urgency(self, draft_projection):
        if self not in draft_projection.free_agents:
            self.urgency = {'urgency': 1, 'display': 'High'}
        elif self in draft_projection.free_agents[:draft_projection.picks_until_next[draft_projection.counter]]:
            self.urgency = {'urgency': 2, 'display': 'Medium'}
        else:
            self.urgency = {'urgency': 3, 'display': 'Low'}
        return self

    def calc_gap(self, replacements):
        replacement = next(r for r in replacements if r.position == self.position)
        self.gap_pts = round(self.fantasy_points - replacement.fantasy_points, 1)
        return self

    def calc_rank(self, free_agents):
        self.rank = free_agents.index(self) + 1
        return self


@app.route("/", methods=['GET', 'POST'])
@app.route("/home", methods=['GET', 'POST'])
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


@app.route("/settings", methods=['GET'])
def settings():
    form = SettingsForm()
    choices = sorted([src.source_name for src in Adp.query.with_entities(Adp.source_name).filter(Adp.season==2022, Adp.system=='1-QB', 
        Adp.scoring=='Half-PPR').distinct()], key=str.casefold)
    choices = ['All (Average)'] + choices
    form.adp_source.choices = choices
    if form.validate_on_submit():
        return redirect(url_for('draft'))
    return render_template('settings.html', title='Settings', form=form)


@app.route("/draft", methods=['POST'])
def draft():
    if 'system' in request.form:
        session.clear()
        season = 2022
        system = request.form['system']
        scoring_format = request.form['scoring_format']
        # projections_source = request.form['projections_source']
        adp_source = request.form['adp_source']
        num_teams = int(request.form['num_teams'])
        roster_size = int(request.form['roster_size'])

        pts_per_rec = {'Half-PPR':0.5, 'PPR':1, 'Non-PPR':0}

        pass_yd = float(request.form['pass_yd'])
        pass_td = float(request.form['pass_td'])
        pass_int = float(request.form['pass_int'])
        rush_yd = float(request.form['rush_yd'])
        rush_td = float(request.form['rush_td'])
        receiv_rec = pts_per_rec[scoring_format]
        receiv_yd = float(request.form['receiv_yd'])
        receiv_td = float(request.form['receiv_td'])
        fumble_lst = float(request.form['fumble_lst'])
        field_goal = float(request.form['field_goal'])
        extra_pt = float(request.form['extra_pt'])
        sack = float(request.form['sack'])
        interception = float(request.form['interception'])
        fumble_recovered = float(request.form['fumble_recovered'])
        def_td = float(request.form['def_td'])
        safety = float(request.form['safety'])


        how_join = 'RIGHT' if system == 'Rookie' else 'LEFT'
        col_join = 'B.player, B.position, A.fantasy_points, B.adp' if system == 'Rookie' else 'A.player, A.position, A.fantasy_points, B.adp'
    
        if adp_source == 'All (Average)':
            adp_query = text(f"""SELECT A.player, A.position, AVG(A.adp) AS adp
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
            """)

        else:
            adp_query = text(f"""SELECT player, position, adp
                             FROM adp
                             WHERE season = {season} 
                             AND system = '{system}'
                             AND scoring = '{scoring_format}'
                             AND source_name = '{adp_source}'
                             AND source_update = (SELECT MAX(source_update) 
                                                     FROM adp 
                                                     WHERE season = {season} 
                                                     AND system = '{system}'
                                                     AND scoring = '{scoring_format}'
                                                     AND source_name = '{adp_source}'
                                                 )
            """)

        query = text(f"""
        SELECT {col_join}
        FROM        
            (SELECT player, position, pass_yd / {pass_yd}
                                    + pass_td * {pass_td}
                                    + pass_int * {pass_int}
                                    + rush_yd / {rush_yd}
                                    + rush_td * {rush_td}
                                    + receiv_rec * {receiv_rec}
                                    + receiv_yd / {receiv_yd}
                                    + receiv_td * {receiv_td} 
                                    + fumble_lst * {fumble_lst} 
                                    + field_goal * {field_goal} 
                                    + extra_pt * {extra_pt}
                                    + sack * {sack}
                                    + interception * {interception} 
                                    + fumble_recovered * {fumble_recovered}  
                                    + def_td * {def_td}
                                    + safety * {safety}
                                    AS fantasy_points
                        FROM projections
                        WHERE season = {season} 
                        AND source_name = 'FantasyPros'
                        AND source_update = (SELECT MAX(source_update) FROM projections WHERE source_name = 'FantasyPros')
            ) A
            {how_join} JOIN
            ({adp_query}
            ) B
            ON (A.player=B.player AND A.position=B.position)
            ORDER BY adp
                 """)
        
        draft_data = pd.DataFrame(db.session.execute(query), columns=['player', 'position', 'fantasy_points', 'adp']) 

        if 'kickers_flag' not in request.form:
            draft_data = draft_data.loc[draft_data['position'] != 'K']
        if 'defenses_flag' not in request.form:
            draft_data = draft_data.loc[draft_data['position'] != 'DST']

        draft_data['fantasy_points'] =  draft_data['fantasy_points'].astype(float).round(1)
        draft_data['adp'] =  draft_data['adp'].astype(float).round(1).fillna(999.9)
        draft_data.fillna(0, inplace=True)
        draft_data.sort_values(by=['adp', 'fantasy_points'], ascending=[True, False], inplace=True)
        free_agents = [NflPlayer(*p) for p in draft_data[['player', 'position', 'adp', 'fantasy_points']].itertuples(index=False, name=None)]
        session['state'] = DraftState(free_agents, system, num_teams, roster_size)
        
        if 'keepers_flag' in request.form:
            return redirect(url_for('keepers'), code=307)
    else:
        keepers = loads(request.form['keepers'])['data']
        df_keepers = pd.DataFrame(keepers)
        df_keepers.drop_duplicates(subset=['player', 'position'], keep='first', inplace=True)
        df_keepers.drop_duplicates(subset=['team', 'round'], keep='first', inplace=True)
        keepers = df_keepers.to_dict('records')
        session['state'].assign_keepers(keepers)

    draft_head = ['', 'Rk', 'Player', 'Pos', 'FPts', 'Gap', 'ADP', 'Urgency']
    repl_head = ['Player', 'Pos', 'FPts', 'ADP']
    team_head = ['Pos', 'Player']

    return render_template('draft.html', title='Draft',
                        draft_head=draft_head,
                        repl_head=repl_head, 
                        team_head=team_head
                    )


@app.route("/draft_data", methods=['GET', 'POST'])
def draft_data():
    if request.method == 'POST' and 'player' in request.form: 
        selection = request.form['player']
        session['state'].make_selection(selection)
    elif request.method == 'POST' and 'player' not in request.form:
        session['state'].undo_selection()

    counter = session['state'].counter
    free_agents = session['state'].free_agents
    picks_until_next = session['state'].picks_until_next
    positions = {p.position for p in free_agents}
    
    if session['state'].system in ['1-QB', '2-QB']:
        state_copy = deepcopy(session['state'])
        replacements = state_copy.get_replacements(positions)
        free_agents = [p.calc_urgency(state_copy).calc_gap(replacements) for p in free_agents]
    else: 
        replacements = []
        for pos in positions:
            replacement = next((r for r in free_agents[picks_until_next[counter]:] if r.position == pos), NflPlayer('N/A', pos, 999.9, 0))
            replacements.append(replacement) 
        free_agents = [p.calc_urgency_adp(counter, picks_until_next, free_agents).calc_gap(replacements) for p in free_agents]
   
    free_agents.sort(key=lambda x: (x.urgency['urgency'], -x.gap_pts, x.adp))
    free_agents = [p.calc_rank(free_agents).__dict__ for p in free_agents]

    replacements = [r.__dict__ for r in replacements]
    roster = [p.__dict__ for p in session['state'].rosters[session['state'].team_pick - 1]]

    return jsonify({'draftdata': free_agents,
                    'repldata': replacements,
                    'teamdata': roster,
                    'pick_label': 'Current Pick: ' + str(session['state'].pick) + ' - #' + str(session['state'].pick_ov) + ' Overall', 
                    'team_label': 'Team ' + str(session['state'].team_pick),
                    'next_pick_label': 'Next Pick: ' + str(session['state'].next_pick) + ' - #' + str(session['state'].next_pick_ov) + ' Overall',
                    'prev_pick_label': 'Latest Pick: ' + str(session['state'].picks[counter - 1] if counter > 0 else '0.0'),
                    'prev_team_label': 'Made By: Team ' + str(session['state'].team_picks[counter - 1] if counter > 0 else '0'),
                    'prev_player_label': session['state'].rosters[session['state'].team_picks[counter - 1] - 1][-1].player if counter > 0 else 'Player',
                    'prev_pos_label': session['state'].rosters[session['state'].team_picks[counter - 1] - 1][-1].position if counter > 0 else 'Position',
                    'counter': counter,
                    'total_picks': len(session['state'].next_picks) - 1,
                    'total_players': session['state'].total_players,
                    'teams': session['state'].teams,
                    'rounds': session['state'].rounds
                    })


@app.route("/results", methods=['POST'])
def results():
    return render_template('results.html', title='Results', result_head=['Team', 'Pick', 'Player', 'Pos', 'FPts'])


@app.route("/results_data", methods=['GET'])
def results_data():
    resultsdata = []
    for roster in session['state'].rosters:
        roster.sort(key=lambda x: float(x.pick))
        for player in roster:
            resultsdata.append(player.__dict__)
    return jsonify({'data' : resultsdata})


@app.route("/settings/num_rounds/<system>")
def num_rounds(system):
    if system == 'Rookie':
        choices = [*range(3, 6)]
    elif system == 'Dynasty':    
        choices = [*range(20, 31)]
    else:
        choices = [*range(12, 19)]
    return jsonify({'num_rounds': choices})


@app.route("/settings/adp_sources/<system>/<scoring>")
def adp_sources(system, scoring):
    choices = sorted([src.source_name for src in Adp.query.with_entities(Adp.source_name).filter(Adp.season==2022, Adp.system==system, 
        Adp.scoring==scoring).distinct()], key=str.casefold)
    if len(choices) > 1:
        choices = ['All (Average)'] + choices
    return jsonify({'adp_sources': choices})


@app.route("/settings/keepers", methods=['POST'])
def keepers():
    hack = request.data
    keepers_head = ['Player', 'Team', 'Round Cost', '']
    players = sorted([p.player + ' (' + p.position + ')' for p in session['state'].free_agents], key=str.lower)
    teams = session['state'].teams
    rounds = session['state'].rounds
    return render_template('keepers.html', title='Keepers', keepers_head=keepers_head, teams=teams, rounds=rounds, players=players)
