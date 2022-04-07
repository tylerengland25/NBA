import numpy as np
import pandas as pd
import streamlit as st
import datetime
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime


def load_data():
    predict_cols = ['date', 'visitor', 'home', 'random_forest', 'line', 'over', 'under']
    df = pd.read_csv('backend/predictions/3p_predictions.csv')[predict_cols]
    df['date'] = pd.to_datetime(df['date'])
    next_game = df['date'].max()

    df['pick'] = np.where(df['random_forest'] > df['line'], 'Over', 'Under')

    df['prediciton'] = df['random_forest']

    return df, next_game


def picks():
    # Predictions
    df, next_game = load_data()

    # Date
    date = st.date_input('Date: ', next_game)

    # Filter on date
    df = df[df['date'] == datetime(date.year, date.month, date.day)]

    matchups = [f'{row.visitor} @ {row.home}' for index, row in df.iterrows()]

    # Rename
    df = df[['visitor', 'home', 'line', 'prediciton', 'pick']]
    df = df.rename(
        {'visitor': 'Visitor', 'home': 'Home', 'pick': 'Pick', 'prediction': 'Prediction', 'line': 'Line'},
        axis=1
    )
    df = df.dropna(axis=1, how='all')
    st.dataframe(df, 1000, 500)

    return matchups, date


def load_graph_data(category, stat, teams, date):
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
    season_start = datetime(2021, 10, 19)
    end_date = datetime(date.year, date.month, date.day)
    df['date'] = pd.to_datetime(df['date'])
    df = df[(df['date'] >= season_start) & (df['date'] < end_date)]
    df['team'] = np.where(df['team'], df['home'], df['visitor'])

    # Merge in opponents
    df = pd.merge(
        df, df,
        left_on=['date', 'visitor', 'home'],
        right_on=['date', 'visitor', 'home'],
        suffixes=('', '_opp')
    )
    df = df[df['team'] != df['team_opp']]

    home_df = df[df['team'] == teams['home']][['date', col]]
    home_df['sma_10'] = home_df.iloc[:, 1].rolling(window=10).mean()
    visitor_df = df[df['team'] == teams['visitor']][['date', col]]
    visitor_df['sma_10'] = visitor_df.iloc[:, 1].rolling(window=10).mean()

    return home_df, visitor_df


def graph(home_df, visitor_df, teams, stat):
    # Seaborn formatting
    sns.set(rc={"figure.figsize": (15, 10)})
    fig = plt.figure()

    # Team colors
    colors = team_colors(teams)

    sns.lineplot(
        data=home_df,
        x='date',
        y='sma_10',
        color=colors['home'][0],
        label=teams['home']
    )
    sns.lineplot(
        data=visitor_df,
        x='date',
        y='sma_10',
        color=colors['visitor'][1] if colors['home'][0] == colors['visitor'][0] else colors['visitor'][0],
        label=teams['visitor']
    )
    plt.xlabel('Date', fontsize=20)
    plt.ylabel(stat, fontsize=20)
    plt.xticks(fontsize=15, rotation=25)
    plt.yticks(fontsize=15)
    plt.legend(fontsize='20')

    return fig


def team_colors(teams):
    colors = {
        'Portland Trail Blazers': ('red', 'black'),
        'San Antonio Spurs': ('grey', 'black'),
        'Utah Jazz': ('blue', 'yellow'),
        'Golden State Warriors': ('yellow', 'blue'),
        'Houston Rockets': ('red', 'black'),
        'Los Angeles Lakers': ('purple', 'yellow'),
        'Philadelphia 76ers': ('blue', 'red'),
        'Toronto Raptors': ('red', 'black'),
        'Washington Wizards': ('red', 'blue'),
        'Indiana Pacers': ('yellow', 'blue'),
        'Milwaukee Bucks': ('green', 'grey'),
        'Orlando Magic': ('black', 'blue'),
        'Chicago Bulls': ('red', 'black'),
        'Brooklyn Nets': ('black', 'grey'),
        'Dallas Mavericks': ('blue', 'grey'),
        'Cleveland Cavaliers': ('red', 'orange'),
        'Memphis Grizzlies': ('blue', 'grey'),
        'Sacramento Kings': ('purple', 'grey'),
        'New Orleans Pelicans': ('grey', 'blue'),
        'Oklahoma City Thunder': ('orange', 'blue'),
        'Denver Nuggets': ('yellow', 'blue'),
        'Detroit Pistons': ('red', 'blue'),
        'Miami Heat': ('pink', 'black'),
        'Phoenix Suns': ('orange', 'purple'),
        'Charlotte Hornets': ('grey', 'blue'),
        'Atlanta Hawks': ('black', 'red'),
        'New York Knicks': ('orange', 'blue'),
        'Boston Celtics': ('green', 'grey'),
        'Minnesota Timberwolves': ('blue', 'green'),
        'Los Angeles Clippers': ('red', 'blue')
    }

    return {'visitor': colors[teams['visitor']], 'home': colors[teams['home']]}


def graph_matchups(matchups, date):
    # Title
    st.subheader('Team Comparisons:')

    # Matchup
    matchup = st.selectbox('Matchup: ', matchups)

    # Statistical categories Column Design
    cols = st.columns([60, 60])
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
    category = cols[0].selectbox('Stats', ['Scoring', 'Shooting', 'Rebounding', 'Blocks and Steals',
         'Assists and Turnovers', 'Scoring Defense', 'Shooting Defense'])
    stat = cols[1].selectbox(category, stats[category])

    # Graph
    teams = {'visitor': matchup.split('@')[0].strip(), 'home': matchup.split('@')[1].strip()}
    home_df, visitor_df = load_graph_data(category, stat, teams, date)
    fig = graph(home_df, visitor_df, teams, stat)
    st.pyplot(fig)


def app():
    # Header
    st.header('Picks:')

    # Picks
    matchups, date = picks()

    # Graph matchups
    graph_matchups(matchups, date)
