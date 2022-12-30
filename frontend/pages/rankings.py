import pandas as pd
import streamlit as st
from datetime import datetime
import numpy as np


def last_3_dates(df):
    dates = {}
    for team in df['team'].unique():
        last_3 = df[df['team'] == team].sort_values(['date'], ascending=False).iloc[:2, :]['date']
        dates[team] = last_3.tolist()

    return dates


def last_3_avg(df, dates, col):
    last_3 = {'team': [], 'last_3': []}
    for key in dates:
        temp = df[(df['team'] == key) & (df['date'] >= dates[key][-1])].groupby(['team']).aggregate('mean')

        if 'perc' in col:
            temp[col] = (temp[col.split('_')[0]] / temp[col.split('_')[0] + 'a']) * 100

        last_3['team'].append(key)
        last_3['last_3'].append(temp[col].tolist()[0])

    return pd.DataFrame(last_3)


def last_1_avg(df, dates, col):
    # Last 1 game
    last_1 = {'team': [], 'last_1': []}
    for key in dates:
        temp = df[(df['team'] == key) & (df['date'] == dates[key][0])].groupby(['team']).aggregate('mean')

        last_1['team'].append(key)
        last_1['last_1'].append(temp[col].tolist()[0])

    return pd.DataFrame(last_1)


def filter_df(category, stat):
    stat_cols = {'Pts per Game': 'final', '1Q Pts': 'q1', '2Q Pts': 'q2', '3Q Pts': 'q3', '4Q Pts': 'q4',
                 'FG Made per Game': 'fg', 'FG Attempted per Game': 'fga', 'FG %': 'fg_perc',
                 '3P Made per Game': '3p', '3P Attempted per Game': '3pa', '3P %': '3p_perc',
                 'FT Made per Game': 'ft', 'FT Attempted per Game': 'fta', 'FT %': 'ft_perc',
                 'ORB per Game': 'orb', 'DRB per Game': 'drb', 'TRB per Game': 'trb',
                 'Blk per Game': 'blk', 'Stl per Game': 'stl', 'Ast per Game': 'ast', 'TOV per Game': 'tov',
                 'Opponent Pts per Game': 'final_opp',
                 'Opponent 1Q Pts': 'q1_opp', 'Opponent 2Q Pts': 'q2_opp',
                 'Opponent 3Q Pts': 'q3_opp', 'Opponent 4Q Pts': 'q4_opp',
                 'Opponent FG Made per Game': 'fg_opp', 'Opponent FG Attempted per Game': 'fga_opp',
                 'Opponent FG %': 'fg_perc_opp', 'Opponent 3P Made per Game': '3p_opp',
                 'Opponent 3P Attempted per Game': '3pa_opp', 'Opponent 3P %': '3p_perc_opp',
                 'Opponent FT Made per Game': 'ft_opp', 'Opponent FT Attempted per Game': 'fta_opp',
                 'Opponent FT %': 'ft_perc_opp'
                 }

    if category == 'Scoring' or category == 'Scoring Defense':
        df = pd.read_csv('backend/data/scoring.csv').drop(['Unnamed: 0'], axis=1)
    else:
        df = pd.read_csv('backend/data/totals/game_totals.csv').drop(['Unnamed: 0'], axis=1)

    col = stat_cols[stat]

    # 2021 Season
    season_start = datetime(2022, 10, 1)
    df['date'] = pd.to_datetime(df['date'])
    today = datetime(datetime.today().year, datetime.today().month, datetime.today().day)
    df = df[(df['date'] >= season_start) & (df['date'] < today)]
    df['team'] = np.where(df['team'], df['home'], df['visitor'])

    # Merge in opponents
    df = pd.merge(
        df, df,
        left_on=['date', 'visitor', 'home'],
        right_on=['date', 'visitor', 'home'],
        suffixes=('', '_opp')
    )
    df = df[df['team'] != df['team_opp']]

    # Last 3 games
    dates = last_3_dates(df)

    last_3 = last_3_avg(df, dates, col)

    last_1 = last_1_avg(df, dates, col)

    # Filter and group for season average
    df = df.groupby(['team']).aggregate('mean').reset_index()

    if 'perc' in col:
        df[col] = (df[col.split('_')[0]] / df[col.split('_')[0] + 'a']) * 100

    # Merge last 3 and last 1
    df = df[['team', col]]
    df = pd.merge(df, last_3, left_on=['team'], right_on=['team'])
    df = pd.merge(df, last_1, left_on=['team'], right_on=['team'])

    # Sort
    ascend = True if category == 'Shooting Defense' or category == 'Scoring Defense' else False
    df = df.sort_values(col, ascending=ascend)

    df = df.rename({'team': 'Team', col: '2022', 'last_3': 'Last 3', 'last_1': 'Last 1'}, axis=1)
    df = df.reset_index().drop(['index'], axis=1)
    df.index += 1

    return df


def app():
    # Header
    st.header('Rankings')

    # Statistical categories
    stats = {'Scoring': ['Pts per Game', '1Q Pts', '2Q Pts', '3Q Pts', '4Q Pts'],
             'Shooting': ['FG Made per Game', 'FG Attempted per Game', 'FG %',
                          '3P Made per Game', '3P Attempted per Game', '3P %',
                          'FT Made per Game', 'FT Attempted per Game', 'FT %'],
             'Rebounding': ['ORB per Game', 'DRB per Game', 'TRB per Game'],
             'Blocks and Steals': ['Blk per Game', 'Stl per Game'],
             'Assists and Turnovers': ['Ast per Game', 'TOV per Game'],
             'Scoring Defense': ['Opponent Pts per Game',
                                 'Opponent 1Q Pts', 'Opponent 2Q Pts',
                                 'Opponent 3Q Pts', 'Opponent 4Q Pts'],
             'Shooting Defense': ['Opponent FG Made per Game', 'Opponent FG Attempted per Game', 'Opponent FG %',
                                  'Opponent 3P Made per Game', 'Opponent 3P Attempted per Game', 'Opponent 3P %',
                                  'Opponent FT Made per Game', 'Opponent FT Attempted per Game', 'Opponent FT %']
             }

    category = st.selectbox(
        'Stats',
        ['Scoring', 'Shooting', 'Rebounding', 'Blocks and Steals',
         'Assists and Turnovers', 'Scoring Defense', 'Shooting Defense']
    )

    stat = st.selectbox(
        category,
        stats[category]
    )

    df = filter_df(category, stat)

    st.dataframe(df)



