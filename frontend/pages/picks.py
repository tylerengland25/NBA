import numpy as np
import pandas as pd
import streamlit as st
import datetime
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime
from IPython.display import HTML


def load_data():
    # Predictions
    predict_cols = ['date', 'visitor', 'home', 'random_forest', 'line', 'over', 'under']
    predict_df = pd.read_csv('backend/predictions/3p_predictions.csv').drop(['Unnamed: 0'], axis=1)[predict_cols]
    predict_df['date'] = pd.to_datetime(predict_df['date'])
    next_game = predict_df['date'].max()

    # Schedule
    schedule_df = pd.read_csv('backend/data/schedules/2021.csv').drop(['Unnamed: 0', 'time'], axis=1)
    schedule_df['date'] = pd.to_datetime(schedule_df['date'])

    df = pd.merge(
        schedule_df, predict_df, left_on=['date', 'visitor', 'home'], right_on=['date', 'visitor', 'home'], how='left'
    )

    df['pick'] = np.where(df['random_forest'] > df['line'], 'Over', 'Under')

    df['prediction'] = df['random_forest']

    return df, next_game


def logo_path(team):
    urls = {
        'Portland Trail Blazers': 'https://loodibee.com/wp-content/uploads/nba-portland-trail-blazers-logo-480x480.png',
        'San Antonio Spurs': 'https://loodibee.com/wp-content/uploads/nba-san-antonio-spurs-logo-480x480.png',
        'Utah Jazz': 'https://loodibee.com/wp-content/uploads/nba-utah-jazz-logo-480x480.png',
        'Golden State Warriors': 'https://loodibee.com/wp-content/uploads/nba-golden-state-warriors-logo-2020-480x480.png',
        'Houston Rockets': 'https://loodibee.com/wp-content/uploads/nba-houston-rockets-logo-2020-300x300.png',
        'Los Angeles Lakers': 'https://loodibee.com/wp-content/uploads/nba-los-angeles-lakers-logo-480x480.png',
        'Philadelphia 76ers': 'https://loodibee.com/wp-content/uploads/nba-philadelphia-76ers-logo-480x480.png',
        'Toronto Raptors': 'https://loodibee.com/wp-content/uploads/nba-toronto-raptors-logo-2020-480x480.png',
        'Washington Wizards': 'https://loodibee.com/wp-content/uploads/nba-washington-wizards-logo-480x480.png',
        'Indiana Pacers': 'https://loodibee.com/wp-content/uploads/nba-indiana-pacers-logo-480x480.png',
        'Milwaukee Bucks': 'https://loodibee.com/wp-content/uploads/nba-milwaukee-bucks-logo-480x480.png',
        'Orlando Magic': 'https://loodibee.com/wp-content/uploads/nba-orlando-magic-logo-480x480.png',
        'Chicago Bulls': 'https://loodibee.com/wp-content/uploads/nba-chicago-bulls-logo-480x480.png',
        'Brooklyn Nets': 'https://loodibee.com/wp-content/uploads/nba-brooklyn-nets-logo-480x480.png',
        'Dallas Mavericks': 'https://loodibee.com/wp-content/uploads/nba-dallas-mavericks-logo-480x480.png',
        'Cleveland Cavaliers': 'https://loodibee.com/wp-content/uploads/nba-cleveland-cavaliers-logo-480x480.png',
        'Memphis Grizzlies': 'https://loodibee.com/wp-content/uploads/nba-memphis-grizzlies-logo-480x480.png',
        'Sacramento Kings': 'https://loodibee.com/wp-content/uploads/nba-sacramento-kings-logo-480x480.png',
        'New Orleans Pelicans': 'https://loodibee.com/wp-content/uploads/nba-new-orleans-pelicans-logo-480x480.png',
        'Oklahoma City Thunder': 'https://loodibee.com/wp-content/uploads/nba-oklahoma-city-thunder-logo-480x480.png',
        'Denver Nuggets': 'https://loodibee.com/wp-content/uploads/nba-denver-nuggets-logo-2018-480x480.png',
        'Detroit Pistons': 'https://loodibee.com/wp-content/uploads/nba-detroit-pistons-logo-480x480.png',
        'Miami Heat': 'https://loodibee.com/wp-content/uploads/nba-miami-heat-logo-480x480.png',
        'Phoenix Suns': 'https://loodibee.com/wp-content/uploads/nba-phoenix-suns-logo-480x480.png',
        'Charlotte Hornets': 'https://loodibee.com/wp-content/uploads/nba-charlotte-hornets-logo-480x480.png',
        'Atlanta Hawks': 'https://loodibee.com/wp-content/uploads/nba-atlanta-hawks-logo-480x480.png',
        'New York Knicks': 'https://loodibee.com/wp-content/uploads/nba-new-york-knicks-logo-480x480.png',
        'Boston Celtics': 'https://loodibee.com/wp-content/uploads/nba-boston-celtics-logo-480x480.png',
        'Minnesota Timberwolves': 'https://loodibee.com/wp-content/uploads/nba-minnesota-timberwolves-logo-480x480.png',
        'Los Angeles Clippers': 'https://loodibee.com/wp-content/uploads/nba-la-clippers-logo-480x480.png'
    }

    return urls[team]


def path_to_image_html(path, team):
    width = 40
    html = f'<div><div style="float: left"><img src={path} style=max-height:{width}px;"/></div><div>{team}</div></div>'
    return html


def style_matchups(df):
    # Logos
    df['Home'] = df['Home'].apply(lambda x: path_to_image_html(logo_path(x), x))
    df['Visitor'] = df['Visitor'].apply(lambda x: path_to_image_html(logo_path(x), x))

    df = HTML(
        df.to_html(
            escape=False,
            index=False,
            header=True,
            col_space={'Visitor': 250, 'Home': 250, 'Line': 30, 'Prediction': 30, 'Pick': 30},
            justify='center'
        ).replace(
            '<tr>', '<tr align="center">'
        )
    )

    return df


def picks():
    # Predictions
    df, next_game = load_data()

    # Date
    date = st.date_input('Date: ', next_game)

    # Filter on date
    df = df[df['date'] == datetime(date.year, date.month, date.day)]

    matchups = [f'{row.visitor} @ {row.home}' for index, row in df.iterrows()]

    # Rename
    df = df[['visitor', 'home', 'line', 'prediction', 'pick']]
    df = df.rename(
        {'visitor': 'Visitor', 'home': 'Home', 'pick': 'Pick', 'prediction': 'Prediction', 'line': 'Line'},
        axis=1
    )
    df = df.dropna(axis=1, how='all')

    # Style
    df = style_matchups(df)
    st.write(df)

    return matchups, date


def load_graph_data(category, stat, teams, date, graph_type):
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

    # Date Range
    start_date = datetime(2021, 10, 19)
    end_date = datetime(date.year, date.month, date.day)
    df['date'] = pd.to_datetime(df['date'])
    df = df[(df['date'] >= start_date) & (df['date'] < end_date)]
    df['team'] = np.where(df['team'], df['home'], df['visitor'])

    # Merge in opponents
    df = pd.merge(
        df, df,
        left_on=['date', 'visitor', 'home'],
        right_on=['date', 'visitor', 'home'],
        suffixes=('', '_opp')
    )
    df = df[df['team'] != df['team_opp']]

    # Simple Moving Average
    home_df = df[df['team'] == teams['home']][['date', col]]
    visitor_df = df[df['team'] == teams['visitor']][['date', col]]
    for days in [3, 5, 10, 15]:
        home_df[f'sma_{days}'] = home_df.iloc[:, 1].rolling(window=days).mean()
        visitor_df[f'sma_{days}'] = visitor_df.iloc[:, 1].rolling(window=days).mean()

    home_df = home_df[['date', graph_type]]
    visitor_df = visitor_df[['date', graph_type]]

    return home_df, visitor_df


def graph(home_df, visitor_df, teams, stat, graph_type):
    # Seaborn formatting
    sns.set(rc={"figure.figsize": (15, 10)})
    fig = plt.figure()

    # Team colors
    colors = team_colors(teams)

    sns.lineplot(
        data=home_df,
        x='date',
        y=graph_type,
        color=colors['home'][0],
        label=teams['home']
    )
    sns.lineplot(
        data=visitor_df,
        x='date',
        y=graph_type,
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

    # Category
    category = cols[0].selectbox('Stats', ['Scoring', 'Shooting', 'Rebounding', 'Blocks and Steals',
                                           'Assists and Turnovers', 'Scoring Defense', 'Shooting Defense'])

    # Statistic
    stat = cols[1].selectbox(category, stats[category])

    # Type of graph
    graph_type = st.radio('Graph Type:', ['15 Day SMA', '10 Day SMA', '5 Day SMA', '3 Day SMA'])
    graph_type = f'sma_{graph_type.split(" ")[0]}'

    # Graph
    teams = {'visitor': matchup.split('@')[0].strip(), 'home': matchup.split('@')[1].strip()}
    home_df, visitor_df = load_graph_data(category, stat, teams, date, graph_type)
    fig = graph(home_df, visitor_df, teams, stat, graph_type)
    st.pyplot(fig)


def app():
    # Header
    st.header('Picks:')

    # Picks
    matchups, date = picks()

    # Graph matchups
    graph_matchups(matchups, date)
