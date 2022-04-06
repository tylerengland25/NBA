import pandas as pd
import streamlit as st
from datetime import datetime, date
import numpy as np
from IPython.display import HTML
import seaborn as sns
import matplotlib.pyplot as plt


def load_data():
    # Load data
    schedule = pd.read_csv('backend/data/schedules/2021.csv').drop(['Unnamed: 0'], axis=1)
    schedule['date'] = pd.to_datetime(schedule['date'])
    odds = pd.read_csv('backend/data/odds/odds.csv').drop(['Unnamed: 0'], axis=1)
    odds['date'] = pd.to_datetime(odds['date'])

    df = pd.merge(
        schedule, odds, left_on=['date', 'visitor', 'home'], right_on=['date', 'visitor', 'home']
    )
    # Cast to types
    df['ml_home'] = df['ml_home'].apply(lambda x: int(float(x)))
    df['ml_visitor'] = df['ml_visitor'].apply(lambda x: int(float(x)))
    df['spread'] = df['spread'].apply(lambda x: x if x == 'pk' else float(x))
    df['total'] = df['total'].apply(lambda x: x if x == '-' else float(x))

    next_game = odds['date'].max()
    df = df[df['date'] == next_game].drop(['date'], axis=1)

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
    df['matchup'] = df.apply(lambda row: path_to_image_html(row['logo'], row['matchup']), axis=1)

    # Rename columns to keep
    df = df.rename(
        {'matchup': 'Matchup', 'time': 'Time', 'line': 'Line', 'total': 'Total', 'spread': 'Spread'},
        axis=1
    )

    df = HTML(
        df.to_html(
            escape=False,
            index=False,
            columns=['Matchup', 'Time', 'Line', 'Total', 'Spread'],
            col_space={'Matchup': 350, 'Line': 30, 'Total': 30, 'Spread': 30},
            justify='left'
        )
    )

    return df


def create_matchups(df):
    # Feature engineer spreads and totals
    df['spread_home'] = np.where(df['ml_home'] > 0, df['spread'], df['spread'] * -1)
    df['spread_visitor'] = np.where(df['ml_visitor'] > 0, df['spread'], df['spread'] * -1)
    df['over'] = df['total'].apply(lambda x: '--------' if x == '-' else f'o{x}')
    df['under'] = df['total'].apply(lambda x: '--------' if x == '-' else f'u{x}')

    # Create matchups
    matchups = []
    matchup_deatils = {'logo': [], 'matchup': [], 'time': [], 'line': [], 'spread': [], 'total': []}
    for index, game in df.iterrows():
        matchups.append(f'{game.visitor} @ {game.home}')

        matchup_deatils['logo'].append(logo_path(game.visitor))
        matchup_deatils['logo'].append(logo_path(game.home))

        matchup_deatils['matchup'].append(game.visitor)
        matchup_deatils['matchup'].append(game.home)

        matchup_deatils['time'].append(game.time)
        matchup_deatils['time'].append('')

        matchup_deatils['line'].append(
            f'+{game.ml_visitor}' if game.ml_visitor > 0 else str(game.ml_visitor)
        )
        matchup_deatils['line'].append(
            f'+{game.ml_home}' if game.ml_home > 0 else str(game.ml_home)
        )

        matchup_deatils['spread'].append(
            f'+{game.spread_home}' if game.spread_home > 0 else str(game.spread_home)
        )
        matchup_deatils['spread'].append(
            f'+{game.spread_visitor}' if game.spread_visitor > 0 else str(game.spread_visitor)
        )

        matchup_deatils['total'].append(game.over)
        matchup_deatils['total'].append(game.under)

    df = pd.DataFrame(matchup_deatils)

    # Style matchups
    df = style_matchups(df)

    return matchups, df


def load_graph_data(category, stat, teams):
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


def graph_matchups(matchups):
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
    home_df, visitor_df = load_graph_data(category, stat, teams)
    fig = graph(home_df, visitor_df, teams, stat)
    st.pyplot(fig)


def app():
    # Load data
    df, next_game = load_data()

    # Header
    st.header(f'Matchups ({next_game.month}/{next_game.day}/{next_game.year})')

    # Matchups
    matchups, df = create_matchups(df)
    st.write(df)

    # Graph matchup
    graph_matchups(matchups)



