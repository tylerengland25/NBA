import pandas as pd
import streamlit as st
from IPython.display import HTML
from datetime import datetime


def load_data():
    # Load data
    schedule = pd.read_csv('backend/data/schedules/2021.csv').drop(['Unnamed: 0'], axis=1)
    schedule['date'] = pd.to_datetime(schedule['date'])
    odds = pd.read_csv('backend/data/odds/odds.csv').drop(['Unnamed: 0'], axis=1)
    odds['date'] = pd.to_datetime(odds['date'])

    df = pd.merge(
        schedule, odds, left_on=['date', 'visitor', 'home'], right_on=['date', 'visitor', 'home'], how='left'
    )

    # Cast to types
    df = df.fillna('-')
    df['ml_home'] = df['ml_home'].apply(lambda x: x if x == '-' else int(float(x)))
    df['ml_visitor'] = df['ml_visitor'].apply(lambda x: x if x == '-' else int(float(x)))
    df['spread'] = df['spread'].apply(lambda x: x if x == 'pk' or x == '-' else float(x))
    df['total'] = df['total'].apply(lambda x: x if x == '-' else float(x))

    next_game = odds['date'].max()

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
            header=True,
            columns=['Matchup', 'Time', 'Line', 'Total', 'Spread'],
            col_space={'Matchup': 250, 'Line': 30, 'Total': 30, 'Spread': 30},
            justify='center'
        ).replace(
            '<tr>', '<tr align="center">'
        )
    )

    return df


def spread(ml, s):
    if s == 'pk':
        return s
    elif ml == '-':
        return '--------'
    elif ml > 0:
        return str(s)
    else:
        return str(s * -1)


def schedule(df, date):
    # Filter on date
    df = df[df['date'] == datetime(date.year, date.month, date.day)].drop(['date'], axis=1)

    # Feature engineer spreads and totals
    df['spread_home'] = df[['ml_home', 'spread']].apply(
        lambda row: spread(row['ml_home'], row['spread']),
        axis=1
    )
    df['spread_visitor'] = df[['ml_visitor', 'spread']].apply(
        lambda row: spread(row['ml_visitor'], row['spread']),
        axis=1
    )
    df['over'] = df['total'].apply(lambda x: '--------' if x == '-' else f'o{x}')
    df['under'] = df['total'].apply(lambda x: '--------' if x == '-' else f'u{x}')
    df['ml_visitor'] = df['ml_visitor'].apply(lambda x: '--------' if x == '-' else str(x))
    df['ml_home'] = df['ml_home'].apply(lambda x: '--------' if x == '-' else str(x))

    # Create matchups
    matchup_deatils = {'logo': [], 'matchup': [], 'time': [], 'line': [], 'spread': [], 'total': []}
    for index, game in df.iterrows():
        matchup_deatils['logo'].append(logo_path(game.visitor))
        matchup_deatils['logo'].append(logo_path(game.home))

        matchup_deatils['matchup'].append(game.visitor)
        matchup_deatils['matchup'].append(game.home)

        matchup_deatils['time'].append(game.time)
        matchup_deatils['time'].append('')

        matchup_deatils['line'].append(
            f'+{game.ml_visitor}'
            if '-' not in game.ml_visitor
            else game.ml_visitor
        )
        matchup_deatils['line'].append(
            f'+{game.ml_home}'
            if '-' not in game.ml_home
            else game.ml_home
        )

        matchup_deatils['spread'].append(
            f'+{game.spread_visitor}'
            if '-' not in game.spread_visitor
            else game.spread_visitor
        )
        matchup_deatils['spread'].append(
            f'+{game.spread_home}'
            if '-' not in game.spread_home
            else game.spread_home
        )

        matchup_deatils['total'].append(game.over)
        matchup_deatils['total'].append(game.under)

    df = pd.DataFrame(matchup_deatils)

    # Style
    df = style_matchups(df)

    st.write(df)


def app():
    # Load data
    df, next_game = load_data()

    # Header
    st.header(f'Schedule')

    # Date select
    date = st.date_input('Date: ', next_game)

    # Matchups
    schedule(df, date)
