import pandas as pd
from flask import render_template, url_for, request, redirect, session, jsonify, flash
from flask_mail import Message

from flaskfantasy import app, db, mail
from flaskfantasy.forms import SettingsForm, ContactForm
from flaskfantasy.models import Adp


class DraftState:
    def __init__(self, pick_num, picks, picks_until_next, team_picks, rosters, free_agents, total_picks, total_players):
        self.pick_num = pick_num
        self.picks = picks
        self.picks_until_next = picks_until_next
        self.team_picks = team_picks
        self.rosters = rosters
        self.free_agents = free_agents
        self.total_picks = total_picks
        self.total_players = total_players
        self.pick = picks[pick_num - 1]
        self.next_pick_num =  pick_num + picks_until_next[pick_num - 1]
        self.next_pick =  picks[self.next_pick_num - 1]
        self.team_pick = team_picks[pick_num - 1]
        self.pick_label = 'Current Pick: ' + str(self.pick) + ' - #' + str(self.pick_num) + ' Overall'
        self.team_label = 'Team ' + str(self.team_pick)
        self.next_pick_label = 'Next Pick: ' + str(self.next_pick) + ' - #' + str(self.next_pick_num) + ' Overall'  
        self.prev_pick_label = 'Latest Pick: 0.0'
        self.prev_team_label = 'Made By: Team 0'
        self.prev_player_label = 'Player'
        self.prev_pos_label = 'Position'

    def make_selection(self, player_name):
        player = next(p for p in self.free_agents if p.player == player_name)
        player.pick = self.pick
        player.team = self.team_pick
        self.pick_num += 1
        self.free_agents.remove(player)
        self.rosters[self.team_pick - 1].append(player)
        self.pick = self.picks[self.pick_num - 1]
        self.next_pick_num =  self.pick_num + self.picks_until_next[self.pick_num - 1]
        self.next_pick =  self.picks[self.next_pick_num - 1]
        self.team_pick = self.team_picks[self.pick_num - 1]
        self.pick_label = 'Current Pick: ' + str(self.pick) + ' - #' + str(self.pick_num) + ' Overall'
        self.team_label = 'Team ' + str(self.team_pick)
        self.next_pick_label = 'Next Pick: ' + str(self.next_pick) + ' - #' + str(self.next_pick_num) + ' Overall' 
        self.prev_pick_label = 'Latest Pick: ' + str(self.picks[self.pick_num - 2])
        self.prev_team_label = 'Made By: Team ' + str(self.team_picks[self.pick_num - 2])
        self.prev_player_label = self.rosters[self.team_picks[self.pick_num - 2] - 1][-1].player
        self.prev_pos_label = self.rosters[self.team_picks[self.pick_num - 2] - 1][-1].position

    def undo_selection(self):
        self.pick_num -= 1
        self.team_pick = self.team_picks[self.pick_num - 1]
        player = self.rosters[self.team_pick - 1][-1]
        player.pick = None
        player.team = None
        self.free_agents.append(player)
        self.free_agents.sort(key=lambda x: x.adp)
        self.rosters[self.team_pick - 1].remove(player)
        self.pick = self.picks[self.pick_num - 1]
        self.next_pick_num =  self.pick_num + self.picks_until_next[self.pick_num - 1]
        self.next_pick =  self.picks[self.next_pick_num - 1]
        self.pick_label = 'Current Pick: ' + str(self.pick) + ' - #' + str(self.pick_num) + ' Overall'
        self.team_label = 'Team ' + str(self.team_pick)
        self.next_pick_label = 'Next Pick: ' + str(self.next_pick) + ' - #' + str(self.next_pick_num) + ' Overall' 
        self.prev_pick_label = 'Latest Pick: ' + (str(self.picks[self.pick_num - 2]) if self.pick_num > 1 else '0.0')
        self.prev_team_label = 'Made By: Team ' + (str(self.team_picks[self.pick_num - 2]) if self.pick_num > 1 else '0')
        self.prev_player_label = self.rosters[self.team_picks[self.pick_num - 2] - 1][-1].player if self.pick_num > 1 else 'Player'
        self.prev_pos_label = self.rosters[self.team_picks[self.pick_num - 2] - 1][-1].position if self.pick_num > 1 else 'Position'    


class NflPlayer:
    def __init__(self, player, position, adp, fantasy_points, gap_pts=None, gap_pct=None, urgency=None, pick=None, team=None):
        self.player = player
        self.position = position
        self.adp = adp
        self.fantasy_points = fantasy_points
        self.gap_pts = gap_pts
        self.gap_pct = gap_pct
        self.urgency = urgency
        
    def __repr__(self):
        return "|".join([self.player, self.position])

    def calc_urgency(self, pick_num, picks_until_next):
        if self.adp <= pick_num + picks_until_next[pick_num - 1]:
            self.urgency = {'urgency': 1, 'display': 'High'}
        elif self.adp >= pick_num + picks_until_next[pick_num - 1] + picks_until_next[pick_num + picks_until_next[pick_num - 1] - 1]:
            self.urgency = {'urgency': 3, 'display': 'Low'}
        else:
            self.urgency = {'urgency': 2, 'display': 'Medium'}
        return self

    def calc_gap(self, replacements):
        replacement = next(r for r in replacements if r.position == self.position)
        self.gap_pts = self.fantasy_points - replacement.fantasy_points
        self.gap_pct = (self.fantasy_points - replacement.fantasy_points) / replacement.fantasy_points * 100
        return self


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
    choices = sorted([src.source_name for src in Adp.query.with_entities(Adp.source_name).filter(Adp.season==2022, Adp.system=='1-QB', 
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
        # projections_source = request.form['projections_source']
        adp_source = request.form['adp_source']
        num_teams = int(request.form['num_teams'])
        roster_size = int(request.form['roster_size']) + 2 #Two extra rounds, so we have something to compare to in the last round

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

        picks = []
        picks_until_next = []    
        for i in range(1, roster_size + 1):
            for j in range(1, num_teams + 1):
                picks.append(str(i) + '.' + str(j))
            picks_until_next += reversed(range(1, num_teams * 2, 2))
        picks_until_next = [num_teams * 2 if n == 1 else n for n in picks_until_next]
        
        team_picks = []
        for j in range(1, roster_size + 1):
            if j % 2 == 0:
                team_picks += reversed(range(1, num_teams + 1))
            else:
                team_picks += range(1, num_teams + 1)
        
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
                             AND source_name = '{adp_source}'
                             AND source_update = (SELECT MAX(source_update) 
                                                     FROM adp 
                                                     WHERE season = {season} 
                                                     AND system = '{system}'
                                                     AND scoring = '{scoring_format}'
                                                     AND source_name = '{adp_source}'
                                                 )
            """    

        query = f"""
        SELECT {col_join}
        FROM        
            (SELECT player, position, pass_yd    / {pass_yd}
                                    + pass_td    * {pass_td}
                                    + pass_int   * {pass_int}
                                    + rush_yd    / {rush_yd}
                                    + rush_td    * {rush_td}
                                    + receiv_rec * {receiv_rec}
                                    + receiv_yd  / {receiv_yd}
                                    + receiv_td  * {receiv_td} 
                                    + fumble_lst * {fumble_lst} AS fantasy_points
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
            ORDER BY adp
                 """
        
        draft_data = pd.DataFrame(db.session.execute(query), columns=['player', 'position', 'fantasy_points', 'adp'])      
        draft_data['fantasy_points'] =  draft_data['fantasy_points'].astype(float).round(1)
        draft_data['adp'] =  draft_data['adp'].astype(float).round(1).fillna(999.9)
        draft_data.fillna(0, inplace=True)
        draft_head = ['', 'Player', 'Pos', 'FPts', 'Gap', 'Gap %', 'ADP', 'Urgency']
        repl_head = ['Player', 'Pos', 'FPts', 'ADP']
        team_head = ['Pos', 'Player']
        total_picks = (roster_size - 2) * num_teams
        total_players = len(draft_data)
        rosters = [[] for _ in range(num_teams)] #Empty rosters to start with
        free_agents = [NflPlayer(*p) for p in draft_data[['player', 'position', 'adp', 'fantasy_points']].itertuples(index=False, name=None)]
        state = DraftState(1, picks, picks_until_next, team_picks, rosters, free_agents, total_picks, total_players)
        session['state'] = state

        return render_template('draft.html', title='Draft', 
                                draft_head=draft_head,
                                repl_head=repl_head, 
                                team_head=team_head,
                                pick_label=state.pick_label, 
                                team_label=state.team_label,
                                next_pick_label=state.next_pick_label,
                                prev_pick_label=state.prev_pick_label,
                                prev_team_label=state.prev_team_label,
                                prev_player_label=state.prev_player_label,
                                prev_pos_label=state.prev_pos_label
                            )
    else:
        return redirect(url_for('settings'))


@app.route("/draft_data", methods=['GET', 'POST'])
def draft_data():
    if request.method == 'POST' and 'player' in request.form: 
        selection = request.form['player']
        session['state'].make_selection(selection)
    elif request.method == 'POST' and 'player' not in request.form:
        session['state'].undo_selection()

    pick_num = session['state'].pick_num
    free_agents = session['state'].free_agents
    next_pick_in = session['state'].picks_until_next
    replacements = []
    for pos in ['QB', 'WR', 'RB', 'TE']:
        replacement = next(r for r in free_agents[next_pick_in[pick_num - 1]:] if r.position == pos)
        replacements.append(replacement)
    free_agents = [p.calc_urgency(pick_num, next_pick_in).calc_gap(replacements).__dict__ for p in free_agents]
    replacements = [r.__dict__ for r in replacements]
    roster = [p.__dict__ for p in session['state'].rosters[session['state'].team_pick - 1]]

    return jsonify({'draftdata': free_agents,
                    'repldata': replacements,
                    'teamdata': roster,
                    'pick_label': session['state'].pick_label,
                    'next_pick_label': session['state'].next_pick_label,
                    'team_label': session['state'].team_label,
                    'prev_pick_label': session['state'].prev_pick_label,
                    'prev_team_label': session['state'].prev_team_label,
                    'prev_player_label': session['state'].prev_player_label,
                    'prev_pos_label': session['state'].prev_pos_label,
                    'pick_num': pick_num,
                    'total_picks': session['state'].total_picks,
                    'total_players': session['state'].total_players
                    })


@app.route("/results", methods=['GET', 'POST'])
def results():
    if request.method == "POST":
        return render_template('results.html', title='Draft', result_head=['Team', 'Pick', 'Player', 'Pos', 'FPts'])
    else:
        return redirect(url_for('settings'))


@app.route("/results_data", methods=['GET'])
def results_data():
    resultsdata = []
    for roster in session['state'].rosters:
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
        choices = [*range(10, 17)]
    return jsonify({'num_rounds': choices})


@app.route("/settings/adp_sources/<system>/<scoring>")
def adp_sources(system, scoring):
    choices = sorted([src.source_name for src in Adp.query.with_entities(Adp.source_name).filter(Adp.season==2022, Adp.system==system, 
        Adp.scoring==scoring).distinct()], key=str.casefold)
    if system == '1-QB':
        choices = ['All (Average)'] + choices
    return jsonify({'adp_sources': choices})
