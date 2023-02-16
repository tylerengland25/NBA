import pandas as pd
from bs4 import BeautifulSoup
from urllib.request import urlopen
from datetime import datetime, date
import ssl
import re


def preprocess_dates(df, season):
    dates = []
    october = season
    for index, row in df.iterrows():
        month = int(str(row['date'])[:-2])
        day = int(str(row['date'])[-2:])
        year = season if month >= 10 else season + 1

        if season == 2019 and month == 11:
            october = season + 1

        year = october if month == 10 else year

        dates.append(date(year, month, day))
    df['date'] = dates

    return df


def preprocess_teams(series, type='city_to_team'):
    city_to_team = {
        'Portland': 'Portland Trail Blazers', 'SanAntonio': 'San Antonio Spurs', 'Utah': 'Utah Jazz',
        'GoldenState': 'Golden State Warriors', 'Houston': 'Houston Rockets', 'LALakers': 'Los Angeles Lakers',
        'Philadelphia': 'Philadelphia 76ers', 'Toronto': 'Toronto Raptors', 'Washington': 'Washington Wizards',
        'Indiana': 'Indiana Pacers', 'Milwaukee': 'Milwaukee Bucks', 'Orlando': 'Orlando Magic',
        'Chicago': 'Chicago Bulls', 'NewJersey': 'Brooklyn Nets', 'Dallas': 'Dallas Mavericks',
        'Cleveland': 'Cleveland Cavaliers', 'Memphis': 'Memphis Grizzlies', 'Sacramento': 'Sacramento Kings',
        'NewOrleans': 'New Orleans Pelicans', 'Seattle': 'Oklahoma City Thunder', 'Denver': 'Denver Nuggets',
        'Detroit': 'Detroit Pistons',  'Miami': 'Miami Heat',  'Phoenix': 'Phoenix Suns',
        'Charlotte': 'Charlotte Hornets', 'Atlanta': 'Atlanta Hawks', 'NewYork': 'New York Knicks',
        'Boston': 'Boston Celtics', 'Minnesota': 'Minnesota Timberwolves', 'LAClippers': 'Los Angeles Clippers',
        'OklahomaCity': 'Oklahoma City Thunder', 'Brooklyn': 'Brooklyn Nets', 'Oklahoma City': 'Oklahoma City Thunder',
        'LA Clippers': 'Los Angeles Clippers', 'LA Lakers': 'Los Angeles Lakers',
        'Golden State': 'Golden State Warriors'
    }
    team_to_city = {}

    for key in city_to_team:
        if key == 'Portland':
            team_to_city['Trail Blazers'] = city_to_team[key]
        else:
            team_to_city[city_to_team[key].split(' ')[-1]] = city_to_team[key]

    if type == 'city_to_team':
        series = series.apply(lambda x: city_to_team[x])
    elif type == 'team_to_city':
        series = series.apply(lambda x: team_to_city[x])

    return series


def preprocess_odds(df):
    visitors_df = df[df['vh'] == 'V'].reset_index().drop(['index'], axis=1)
    home_df = df[df['vh'] == 'H'].reset_index().drop(['index'], axis=1)
    df = pd.merge(visitors_df, home_df, left_index=True, right_index=True, suffixes=('_v', '_h'))
    df['total'] = df['open_v']
    df['spread'] = df['open_h']
    df = df[['date_v', 'team_v', 'ml_v', 'team_h', 'ml_h', 'total', 'spread']]
    df = df.rename(
        {'date_v': 'date',
         'team_v': 'visitor', 'ml_v': 'ml_visitor',
         'team_h': 'home', 'ml_h': 'ml_home',
         'total': 'total', 'spread': 'spread'
         },
        axis=1
    )

    return df


def preprocess_season(season):
    df = pd.read_excel(f'backend/data/odds/{season}.xlsx')

    df = df[['Date', 'VH', 'Team', 'Open', 'ML']]
    df = df.rename({'Date': 'date', 'VH': 'vh', 'Team': 'team', 'Open': 'open', 'ML': 'ml'}, axis=1)

    df = preprocess_dates(df, season)
    df['team'] = preprocess_teams(df['team'], type='city_to_team')
    df = preprocess_odds(df)

    return df


def combine_odds():
    # Combine odds into one dataframe
    df = pd.DataFrame()
    for season in range(2007, 2022):
        df = df.append(preprocess_season(season), ignore_index=True)

    df.to_csv('backend/data/odds/odds.csv')


def scrape_latest():
    # Connect to website
    ssl._create_default_https_context = ssl._create_unverified_context
    url = 'https://sportsdata.usatoday.com/basketball/nba/odds'
    html = urlopen(url)
    soup = BeautifulSoup(html, features="lxml")

    # Dataframe
    df = pd.DataFrame()

    # Date
    next_date = soup.find('div', attrs={'class': 'class-Rj1m2E0'}).find('h3').text
    next_date = f'{next_date}/{date.today().year}'
    next_date = datetime.strptime(next_date, '%a, %b/%d/%Y')

    games = soup.find_all('tbody')
    for game in games:
        teams = game.find_all('tr')
        visitors = teams[0].find_all('td')
        home = teams[1].find_all('td')

        # Teams
        visitor_team = [data.text for data in visitors[0].find_all('div')][-1]
        home_team = [data.text for data in home[0].find_all('div')][-1]

        # Moneylines
        visitor_ml = int([data.text for data in visitors[2].find_all('span')][0])
        home_ml = int([data.text for data in home[2].find_all('span')][0])

        # Spreads
        spread = float([data.text for data in visitors[1].find_all('span')][1].strip('+-'))

        # Totals
        total = [data.text for data in visitors[3].find_all('span')]
        total = float(total[1].strip('OU')) if len(total) >= 2 else total[0]

        row = {'date': date(next_date.year, next_date.month, next_date.day),
               'visitor': visitor_team, 'ml_visitor': visitor_ml,
               'home': home_team, 'ml_home': home_ml,
               'total': total, 'spread': spread}

        df = df.append(row, ignore_index=True)

    return df


def update_odds():
    df = pd.read_csv('backend/data/odds/odds.csv').drop(['Unnamed: 0'], axis=1)

    latest_odds = scrape_latest()
    latest_odds['visitor'] = preprocess_teams(latest_odds['visitor'], type='team_to_city')
    latest_odds['home'] = preprocess_teams(latest_odds['home'], type='team_to_city')

    df = df.append(latest_odds, ignore_index=True)
    df['date'] = pd.to_datetime(df['date'])
    df = df.drop_duplicates(['date', 'visitor', 'home'], keep='last')

    df.to_csv('backend/data/odds/odds.csv')


if __name__ == '__main__':
    update_odds()
