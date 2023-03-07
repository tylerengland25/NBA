from bs4 import BeautifulSoup
from urllib.request import urlopen
import pandas as pd
from datetime import date


def scrape_game(link, game_data):
    # Initialize dataframe
    game_df = pd.DataFrame()

    # Connect to website
    link = link.split('/')
    link.insert(2, 'shot-chart')
    url = f"https://www.basketball-reference.com{'/'.join(link)}"
    html = urlopen(url)
    soup = BeautifulSoup(html, features="lxml")

    # Find shooting table and return quarter shooting stats for both teams
    tables = soup.find_all('table')
    team = 0
    for table in tables:
        rows = []
        quarters = table.find_all('tr')
        for quarter in quarters[1:]:
            data = quarter.find_all(['th', 'td'])
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
            
            row = {
                'date': game_data['date'], 'visitor': game_data['visitor'], 'home': game_data['home'], 'team': team, 'quarter': quarter, 
                'fg': data[1], 'fga': data[2], 'fg_perc': data[3], '2p': data[4], '2pa': data[5], '2p_perc': data[6], 
                '3p': data[7], '3pa': data[8], '3p_perc': data[9], 'efg_perc': data[10], 'ast': data[11], 'ast_perc': data[12]
            }
            rows.append(row)

        rows = pd.DataFrame(rows)
        game_df = pd.concat([game_df, rows], axis=0, ignore_index=True)
        team = 1

    return game_df


def scrape_month(season, month, latest_date, current_date):
    # Print month
    print("\t" + month)

    # Connect to website
    url = "https://www.basketball-reference.com/leagues/NBA_{}_games-{}.html".format(str(season), month)
    html = urlopen(url)
    soup = BeautifulSoup(html, features="lxml")

    # Initialize dataframe
    month_df = pd.DataFrame()

    # Find games and iterate to find shooting data
    games = soup.find("table").find_all("tr")[1:]
    for game in games:
        row_data = game.find_all(["th", "td"])
        if len(row_data) > 1:
            # Print game info
            game_data = {'date': row_data[0].text, 'visitor': row_data[2].text, 'home': row_data[4].text}
            print(f"\t\t{game_data['date']}, {game_data['visitor']} @ {game_data['home']}")

            # Check if game date is between latest date and current date
            game_date = pd.to_datetime(game_data['date'])
            game_date = date(game_date.year, game_date.month, game_date.day)

            if latest_date <= game_date < current_date:
                link = row_data[6].a["href"]
                players_df = scrape_game(link, game_data)
                month_df = pd.concat([month_df, players_df], axis=0, ignore_index=True)
            elif game_date > current_date:
                return month_df

    return month_df


def scrape_season(season, months, latest_date, current_date):
    # Print season
    print(season)
    
    # Initialize dataframe
    season_df = pd.DataFrame()

    # Scrape months in season
    for month in months:
        month_df = scrape_month(season + 1, month, latest_date, current_date)
        season_df = pd.concat([season_df, month_df], axis=0, ignore_index=True)

    # Append season to dataframe
    season_df['season'] = season

    return season_df


def update():
    # Load data
    df = pd.read_csv('backend/data/shooting.csv').drop(['Unnamed: 0'], axis=1)

    # Extract latest date
    dates = pd.to_datetime(df['date'])
    latest_date = dates.max()
    latest_date = date(latest_date.year, latest_date.month, latest_date.day)

    # Current date to update until
    current_date = date.today()

    # Season an months to scrape
    season = 2022
    months = ["october", "november", "december", "january", "february", "march"]

    season_df = scrape_season(season, months, latest_date, current_date)
    df = pd.concat([df, season_df], axis=0, ignore_index=True)

    df = df.drop_duplicates(['date', 'visitor', 'home', 'team', 'quarter'], keep='last')
    df.to_csv('backend/data/shooting.csv', index=False)

