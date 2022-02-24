from bs4 import BeautifulSoup
from urllib.request import urlopen
import pandas as pd
from datetime import date


def scrape_game(link, game_data):
    # Connect to website
    link = link.split('/')
    link.insert(2, 'shot-chart')
    url = "https://www.basketball-reference.com{}".format('/'.join(link))
    html = urlopen(url)
    soup = BeautifulSoup(html, features="lxml")

    # Game dataframe
    stats = ['team', 'quarter', 'fg', 'fga', 'fg_perc', '2p', '2pa', '2p_perc', '3p', '3pa', '3p_perc', 'efg_perc',
             'ast', 'ast_perc']
    cols = ['date', 'visitor', 'home'] + stats
    game_df = pd.DataFrame(columns=cols)

    # Find shooting table and return quarter shooting stats for both teams
    tables = soup.find_all('table')
    team = 0
    for table in tables:
        rows = table.find_all('tr')
        for row in rows[1:]:
            data = row.find_all(['th', 'td'])
            data = [td.text for td in data]

            # Which quarter
            if data[0] == '1st':
                quarter = 'q1'
            elif data[0] == '2nd':
                quarter = 'q2'
            elif data[0] == '3rd':
                quarter = 'q3'
            elif data[0] == '4th':
                quarter = 'q4'
            elif data[0] == 'OT':
                quarter = 'ot1'
            elif data[0] == '2OT':
                quarter = 'ot2'
            elif data[0] == '3OT':
                quarter = 'ot3'
            elif data[0] == '4OT':
                quarter = 'ot4'
            else:
                quarter = 'total'

            game_df = game_df.append(
                {'date': game_data['date'], 'visitor': game_data['visitor'], 'home': game_data['home'],
                 'team': team, 'quarter': quarter, 'fg': data[1], 'fga': data[2], 'fg_perc': data[3], '2p': data[4],
                 '2pa': data[5], '2p_perc': data[6], '3p': data[7], '3pa': data[8], '3p_perc': data[9],
                 'efg_perc': data[10], 'ast': data[11], 'ast_perc': data[12]},
                ignore_index=True)

        team = 1

    return game_df


def scrape_month(season, month, latest_date, current_date):
    print("\t" + month)
    # Connect to website
    url = "https://www.basketball-reference.com/leagues/NBA_{}_games-{}.html".format(str(season), month)
    html = urlopen(url)
    soup = BeautifulSoup(html, features="lxml")

    # Month datframe
    stats = ['team', 'quarter', 'fg', 'fga', 'fg_perc', '2p', '2pa', '2p_perc', '3p', '3pa', '3p_perc', 'efg_perc',
             'ast', 'ast_perc']
    cols = ['date', 'visitor', 'home'] + stats
    month_df = pd.DataFrame(columns=cols)

    # Find games and iterate to find shooting data
    games = soup.find("table").find_all("tr")[1:]
    for game in games:
        row_data = game.find_all(["th", "td"])
        if len(row_data) > 1:
            print("\t\t" + str(row_data[0].text) + ", " + row_data[2].text + " @ " + row_data[4].text)
            game_data = {'date': row_data[0].text, 'visitor': row_data[2].text, 'home': row_data[4].text}

            # Check if game date is between latest date and current date
            game_date = pd.to_datetime(game_data['date'])
            game_date = {
                'year': pd.to_datetime(game_date).year,
                'month': pd.to_datetime(game_date).month,
                'day': pd.to_datetime(game_date).day
            }
            game_date = date(game_date['year'], game_date['month'], game_date['day'])

            if latest_date <= game_date < current_date:
                link = row_data[6].a["href"]
                month_df = month_df.append(scrape_game(link, game_data), ignore_index=True)
            elif game_date == current_date:
                month_df = month_df.append(
                    {'date': game_data['date'], 'visitor': game_data['visitor'],
                     'home': game_data['home'], 'team': 1, 'quarter': 'total'},
                    ignore_index=True
                )
                month_df = month_df.append(
                    {'date': game_data['date'], 'visitor': game_data['visitor'],
                     'home': game_data['home'], 'team': 0, 'quarter': 'total'},
                    ignore_index=True
                )
            elif game_date > current_date:
                return month_df

    return month_df


def scrape_season(season, months, latest_date, current_date):
    print(season)
    # Season dataframe
    stats = ['team', 'quarter', 'fg', 'fga', 'fg_perc', '2p', '2pa', '2p_perc', '3p', '3pa', '3p_perc', 'efg_perc',
             'ast', 'ast_perc']
    cols = ['date', 'visitor', 'home'] + stats
    season_df = pd.DataFrame(columns=cols)

    # Scrape months in season
    for month in months:
        season_df = season_df.append(scrape_month(season + 1, month, latest_date, current_date), ignore_index=True)

    return season_df


def main():
    df = pd.read_csv('backend/data/shooting.csv').drop(['Unnamed: 0'], axis=1)

    dates = pd.to_datetime(df['date'])

    latest_date = dates.sort_values(axis=0, ascending=False).unique()[0]
    latest_date = {
        'year': pd.to_datetime(latest_date).year,
        'month': pd.to_datetime(latest_date).month,
        'day': pd.to_datetime(latest_date).day
    }

    latest_date = date(latest_date['year'], latest_date['month'], latest_date['day'])

    current_date = date.today()

    season = 2021
    months = ["october", "november", "december", "january", "february", "march", "april"]

    df = df.append(scrape_season(season, months, latest_date, current_date), ignore_index=True)
    df = df.drop_duplicates(['date', 'visitor', 'home', 'team', 'quarter'], keep='last')

    df.to_csv('backend/data/shooting.csv')


if __name__ == '__main__':
    main()
