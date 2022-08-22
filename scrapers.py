from requests import get
import pandas as pd
from bs4 import BeautifulSoup
from sqlalchemy import create_engine
from datetime import datetime
import numpy as np
import os


def parse_defense(player):
    if len(player.split(' ')) < 3:
        dst = player[0:3].upper()
    else:
        dst = ''.join(w[0].upper() for w in player.split(' ')[:-1])
    if dst in ['LA', 'NY']:
        dst = str(dst) + player.split(' ')[-1][0]
    return dst
    

def fftoday_projections(season):
    season = int(season)
    positions = {'QB': '10',
                 'RB': '20',
                 'WR': '30',
                 'TE': '40'}
    # 'K':'80',
    # 'DEF':'99'}
    df_final = pd.DataFrame()
    for position in positions.keys():
        df_pos = pd.DataFrame()
        for page in range(4):
            url = 'https://www.fftoday.com/rankings/playerproj.php?Season={season}&PosID={position}&LeagueID=&order_by=FFPts&sort_order=DESC&cur_page={page}'.format(
                season=season, position=positions[position], page=page)
            response = get(url)
            if response.ok:
                soup = BeautifulSoup(response.text, 'html.parser')
                table = soup.findAll('table')[7]
                df = pd.read_html(str(table))[1]
                df.columns = df.iloc[0].fillna('') + df.iloc[1]
                df.drop([0, 1], inplace=True)
                if df.empty:
                    continue
                df.drop(columns=['Chg', 'FantasyFPts'], inplace=True)
                df.insert(loc=1, column='position', value=position)
                df.rename(columns={df.columns[0]: 'player'}, inplace=True)
                df_pos = pd.concat([df_pos, df])
            else:
                print('Oops, something didn\'t work right', response.status_code)
                return
        df_final = pd.concat([df_final, df_pos], ignore_index=True)
    update = datetime.strptime(soup.find('td', class_='update').text.split()[-1], '%m/%d/%Y')
    df_final['player'].replace(r'\s(?:I+|IV|V|VI|VI+|IX|X|Jr\.|Jr)$', '', regex=True, inplace=True)
    df_final['player'] = np.where(df_final['player'].str.contains(r'^[A-Z]{2}\s'), df_final['player'].apply(
        lambda x: '.'.join(x.split(' ')[0]) + '. ' + ' '.join(x.split(' ')[1:])), df_final['player'])
    df_final.insert(loc=0, column='Season', value=season)
    df_final = df_final.apply(pd.to_numeric, errors='ignore').reset_index(drop=True)
    df_final.fillna(0, inplace=True)
    df_final.drop('Bye', axis=1, inplace=True)
    cols = ['season', 'player', 'position', 'team', 'passing_comp', 'passing_att', 'passing_yard', 'passing_td',
            'passing_int',
            'rushing_att', 'rushing_yard', 'rushing_td',
            'receiving_rec', 'receiving_yard', 'receiving_td']
    df_final.columns = cols
    df_final['source_name'] = 'FFToday'
    df_final['source_update'] = update
    df_final['insert_timestamp'] = datetime.utcnow()

    engine = create_engine(os.environ.get('DATABASE_URL'))
    with engine.begin() as connection:
        df_final.to_sql('projections', con=connection, index=False, if_exists='append')

    print('FFToday_Projections: Season %s\n\n' % season, df_final.head())


def fantasypros_projections(season):
    season = int(season)
    positions = ['qb', 'rb', 'wr', 'te', 'k', 'dst']
    df_final = pd.DataFrame()
    for position in positions:
        url = f'https://www.fantasypros.com/nfl/projections/{position}.php?week=draft'
        response = get(url)
        if response.ok:
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table', {'id': 'data'})
            df = pd.read_html(str(table))[0]
            df.columns = df.columns.map(''.join)
            df.columns = df.columns.str.lower()
            if position != 'dst':
                df['team'] = df[df.columns[0]].apply(lambda x: x.split()[-1])
                df['player'] = df[df.columns[0]].apply(lambda x: ' '.join(x.split()[:-1]))
            else:
                df['team'] = df.apply(lambda x: parse_defense(x['player']), axis=1)
            df['position'] = position.upper()
            df_final = pd.concat([df_final, df])
        else:
            print('Oops, something didn\'t work right', response.status_code)
            return
    update = datetime.strptime(soup.find('time').text, '%b %d, %Y')
    suffix = r'\s(?:I+|IV|V|VI|VI+|IX|X|Jr\.|Jr)$'
    df_final['player'].replace(suffix, '', regex=True, inplace=True)
    df_final['player'].replace('\.', '', regex=True, inplace=True)
    df_final = df_final.apply(pd.to_numeric, errors='ignore').reset_index(drop=True)
    df_final.fillna(0, inplace=True)
    df_final = df_final.rename(columns={'passingatt': 'pass_att',
                                        'passingcmp': 'pass_cmp',
                                        'passingyds': 'pass_yd',
                                        'passingtds': 'pass_td',
                                        'passingints': 'pass_int',
                                        'rushingatt': 'rush_att',
                                        'rushingyds': 'rush_yd',
                                        'rushingtds': 'rush_td',
                                        'receivingrec': 'receiv_rec',
                                        'receivingyds': 'receiv_yd',
                                        'receivingtds': 'receiv_td',
                                        'miscfl': 'fumble_lst',
                                        'fg':'field_goal',
                                        'fga':'field_goal_att',
                                        'xpt':'extra_pt',
                                        'int':'interception',
                                        'fr':'fumble_recovered',
                                        'ff':'forced_fumble',
                                        'td':'def_td',
                                        'pa':'pts_allowed',
                                        'yds agn':'yd_against'
                                        })

    cols = ['player', 'position', 'team',
            'pass_cmp', 'pass_att', 'pass_yd', 'pass_td', 'pass_int',
            'rush_att', 'rush_yd', 'rush_td',
            'receiv_rec', 'receiv_yd', 'receiv_td',
            'fumble_lst',
            'field_goal', 'field_goal_att', 'extra_pt',
            'sack', 'interception', 'fumble_recovered', 'forced_fumble', 'def_td', 'safety', 'pts_allowed', 'yd_against']

    df_final = df_final[cols]
    df_final['season'] = season
    df_final['source_name'] = 'FantasyPros'
    df_final['source_update'] = update
    df_final['insert_timestamp'] = datetime.utcnow()

    engine = create_engine(os.environ.get('DATABASE_URL'))
    with engine.begin() as connection:
        df_final.to_sql('projections', con=connection, index=False, if_exists='append')

    print('FantasyPros_Projections: Season %s\n\n' % season, df_final.head())


def fantasypros_adp(season):
    season = int(season)
    scoring = {'Non-PPR': 'overall', 'Half-PPR': 'half-point-ppr-overall', 'PPR': 'ppr-overall'}
    systems = {'Rookie': 'rookies', 'Dynasty': 'dynasty-overall'}
    df_final = pd.DataFrame()
    for sc in scoring.keys():
        url = f'https://www.fantasypros.com/nfl/adp/{scoring[sc]}.php?year={season}'
        response = get(url)
        if response.ok:
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table', {'id': 'data'})
            df = pd.read_html(str(table))[0]
            df['player'] = df['Player Team (Bye)'].apply(lambda x: ' '.join(x.split()[:-1]) if x.split()[-1] == 'O' else x)  # Removes letter O from player name when he is 'Out'
            df['team'] = df['player'].apply(lambda x: ''.join(x.split()[-2]) if len(x.split()) > 3 else np.nan)
            df['player'] = df['player'].apply(lambda x: ' '.join(x.split()[:-2]) if len(x.split()) > 3 else x)  # Removes team and bye week from the player's name while leaving 'Jr.' and 'II'
            df['position'] = df['POS'].apply(lambda x: ''.join([i for i in x if not i.isdigit()]))  # Removes the positional ranking
            df.drop(['Rank', 'Player Team (Bye)', 'POS', 'AVG'], axis=1, inplace=True)
            df = pd.melt(df, id_vars=['player', 'position', 'team'], var_name='source_name', value_name='adp')
            df['source_name'] = df['source_name']
            df = df.loc[df['source_name'] != 'FFC']
            df = df.loc[df['adp'].notnull()]
            df['scoring'] = sc
            df['system'] = '1-QB'
            df_final = pd.concat([df_final, df], ignore_index=True)
        else:
            print('Oops, something didn\'t work right', response.status_code)
            return
    for sy in systems.keys():
        url = f'https://www.fantasypros.com/nfl/adp/{systems[sy]}.php?year={season}'
        response = get(url)
        if response.ok:
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table', {'id': 'data'})
            df = pd.read_html(str(table))[0]
            df['player'] = df['Player Team (Bye)'].apply(lambda x: ' '.join(x.split()[:-1]) if x.split()[-1] == 'O' else x)  # Removes letter O from player name when he is 'Out'
            df['team'] = df['player'].apply(lambda x: ''.join(x.split()[-2]) if len(x.split()) > 3 else np.nan)
            df['player'] = df['player'].apply(lambda x: ' '.join(x.split()[:-2]) if len(x.split()) > 3 else x)  # Removes team and bye week from the player's name while leaving 'Jr.' and 'II'
            df['position'] = df['POS'].apply(lambda x: ''.join([i for i in x if not i.isdigit()]))  # Removes the positional ranking
            df.drop(['Rank', 'Player Team (Bye)', 'POS'], axis=1, inplace=True)
            df = df.rename(columns={'AVG': 'adp'})
            df['source_name'] = 'FantasyPros'
            df['system'] = sy
            df['key'] = 0
            df_scoring = pd.DataFrame(data=scoring.keys(), columns=['scoring'])
            df_scoring['key'] = 0
            df = df.merge(df_scoring, on='key').drop('key', axis=1)
            df_final = pd.concat([df_final, df], ignore_index=True)
        else:
            print('Oops, something didn\'t work right', response.status_code)
            return       
    update = datetime.utcnow()
    suffix = r'\s(?:I+|IV|V|VI|VI+|IX|X|Jr\.|Jr)$'
    df_final['player'].replace(suffix, '', regex=True, inplace=True)
    df_final['player'].replace('\.', '', regex=True, inplace=True)
    df_final['team'] = np.where(df_final['position'] == 'DST', df_final.apply(lambda x: parse_defense(x['player']), axis=1), df_final['team'])
    df_final['season'] = season
    cols = ['player', 'position', 'team', 'adp', 'scoring', 'system', 'season', 'source_name']
    df_final = df_final[cols]
    df_final['source_update'] = update
    df_final['insert_timestamp'] = datetime.utcnow()
    engine = create_engine(os.environ.get('DATABASE_URL'))
    with engine.begin() as connection:
        df_final.to_sql('adp', con=connection, index=False, if_exists='append')
    print('FantasyPros_ADP: Season %s\n\n' % season, df_final.head())


def fantasyfootballcalc_adp(season):
    season = int(season)
    scoring = {'Non-PPR': 'standard', 'Half-PPR': 'half-ppr', 'PPR': 'ppr'}
    systems = {'2-QB': '2qb', 'Rookie': 'rookie', 'Dynasty': 'dynasty'}
    df_final = pd.DataFrame()
    for sc in scoring.keys():
        response = get(f'https://fantasyfootballcalculator.com/api/v1/adp/{scoring[sc]}?teams=12&year={season}')
        if response.ok:
            packages_json = response.json()
            if packages_json['status'] == 'Success':
                update = packages_json['meta']['end_date']
                update = datetime.strptime(update, '%Y-%m-%d')
                df = pd.DataFrame.from_dict(packages_json['players'])
                df['scoring'] = sc
                df['system'] = '1-QB'
                df['source_update'] = update
                df_final = pd.concat([df_final, df])
            else:
                print(packages_json['errors'])
                return
        else:
            print('Oops, something didn\'t work right', response.status_code)
            return
    for sy in systems.keys():
        response = get(f'https://fantasyfootballcalculator.com/api/v1/adp/{systems[sy]}?teams=12&year={season}')
        if response.ok:
            packages_json = response.json()
            update = packages_json['meta']['end_date']
            update = datetime.strptime(update, '%Y-%m-%d')
            df = pd.DataFrame.from_dict(packages_json['players'])
            df['system'] = sy
            df['key'] = 0
            df_scoring = pd.DataFrame(data=scoring.keys(), columns=['scoring'])
            df_scoring['key'] = 0
            df = df.merge(df_scoring, on='key').drop('key', axis=1)
            df['source_update'] = update
            df_final = pd.concat([df_final, df])
        else:
            print('Oops, something didn\'t work right', response.status_code)
            return    
    df_final = df_final.loc[df_final['name'] != 'Deleted Deleted']
    df_final['name'].replace(r'\s(?:I+|IV|V|VI|VI+|IX|X|Jr\.|Jr)$', '', regex=True, inplace=True)    
    df_final['name'].replace('\.', '', regex=True, inplace=True)
    fantasypros_names = {'Arizona Defense':'Arizona Cardinals',
                     'Atlanta Defense':'Atlanta Falcons',
                     'Baltimore Defense':'Baltimore Ravens',
                     'Buffalo Defense':'Buffalo Bills',
                     'Carolina Defense':'Carolina Panthers',
                     'Chicago Defense':'Chicago Bears',
                     'Cincinnati Defense':'Cincinnati Bengals',
                     'Cleveland Defense':'Cleveland Browns',
                     'Dallas Defense':'Dallas Cowboys',
                     'Denver Defense':'Denver Broncos',
                     'Detroit Defense':'Detroit Lions',
                     'Green Bay Defense':'Green Bay Packers',
                     'Houston Defense':'Houston Texans',
                     'Indianapolis Defense':'Indianapolis Colts',
                     'Jacksonville Defense':'Jacksonville Jaguars',
                     'Kansas City Defense':'Kansas City Chiefs',
                     'Las Vegas Defense':'Las Vegas Raiders',
                     'LA Chargers Defense':'Los Angeles Chargers',
                     'LA Rams Defense':'Los Angeles Rams',
                     'Miami Defense':'Miami Dolphins',
                     'Minnesota Defense':'Minnesota Vikings',
                     'New England Defense':'New England Patriots',
                     'New Orleans Defense':'New Orleans Saints',
                     'NY Giants Defense':'New York Giants',
                     'NY Jets Defense':'New York Jets',
                     'Philadelphia Defense':'Philadelphia Eagles',
                     'Pittsburgh Defense':'Pittsburgh Steelers',
                     'San Francisco Defense':'San Francisco 49ers',
                     'Seattle Defense':'Seattle Seahawks',
                     'Tampa Bay Defense':'Tampa Bay Buccaneers',
                     'Tennessee Defense':'Tennessee Titans',
                     'Washington Defense':'Washington Commanders',
                     'Pat Mahomes':'Patrick Mahomes', 
                     'Kenneth Walker':'Ken Walker'}
    df_final['name'].replace(fantasypros_names, inplace=True)
    df_final['position'].replace({'DEF':'DST', 'PK':'K'}, inplace=True)
    df_final['team'].replace({'JAX':'JAC', 'FA':np.nan}, inplace=True)
    df_final['season'] = season
    df_final.rename(columns={'name': 'player'}, inplace=True)
    cols = ['player', 'position', 'team', 'adp', 'scoring', 'system', 'season', 'source_update']
    df_final = df_final[cols]
    df_final['source_name'] = 'FFC'
    df_final['insert_timestamp'] = datetime.utcnow()
    engine = create_engine(os.environ.get('DATABASE_URL'))
    with engine.begin() as connection:
        df_final.to_sql('adp', con=connection, index=False, if_exists='append')

    print('FantasyFootballCalculator_ADP: Season %s\n\n' % season, df_final.head())
