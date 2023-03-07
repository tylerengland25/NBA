from bs4 import BeautifulSoup
from urllib.request import urlopen
import re
import pandas as pd
from datetime import date


def scrape_game(link, game_data):
    # Initialize dataframe
    game_df = pd.DataFrame()

    # Connect to website
    url = f"https://www.basketball-reference.com{link}"
    html = urlopen(url)
    soup = BeautifulSoup(html, features="lxml")

    # Find scoring table and return quarter scores for both teams
    scoring_tag = soup.find('div', attrs={'class': 'content_grid'}).find('div')
    table_data = re.findall("(?<=\>)(\d*?)(?=\</td>)", str(scoring_tag))
    scores = []
    for td in table_data:
        if len(td) > 0:
            scores.append(int(td))

    if len(scores) == 8:
        home_row = {
            'date': game_data['date'], 'visitor': game_data['visitor'], 'home': game_data['home'],
            'team': 1, 'q1': scores[4], 'q2': scores[5], 'q3': scores[6], 'q4': scores[7],
            'final': game_data['home_final']
        }
        visitor_row = {
            'date': game_data['date'], 'visitor': game_data['visitor'], 'home': game_data['home'],
            'team': 0, 'q1': scores[0], 'q2': scores[1], 'q3': scores[2], 'q4': scores[3],
            'final': game_data['visitor_final']
        }
    elif len(scores) == 10:
        home_row = {
            'date': game_data['date'], 'visitor': game_data['visitor'], 'home': game_data['home'],
            'team': 1, 'q1': scores[5], 'q2': scores[6], 'q3': scores[7], 'q4': scores[8],
            'ot1': scores[9],
            'final': game_data['home_final']
        }
        visitor_row = {
            'date': game_data['date'], 'visitor': game_data['visitor'], 'home': game_data['home'],
            'team': 0, 'q1': scores[0], 'q2': scores[1], 'q3': scores[2], 'q4': scores[3],
            'ot1': scores[4],
            'final': game_data['visitor_final']
        }
    elif len(scores) == 12:
        home_row = {
            'date': game_data['date'], 'visitor': game_data['visitor'], 'home': game_data['home'],
            'team': 1, 'q1': scores[6], 'q2': scores[7], 'q3': scores[8], 'q4': scores[9],
            'ot1': scores[10], 'ot2': scores[11],
            'final': game_data['home_final']
        }
        visitor_row = {
            'date': game_data['date'], 'visitor': game_data['visitor'], 'home': game_data['home'],
            'team': 0, 'q1': scores[0], 'q2': scores[1], 'q3': scores[2], 'q4': scores[3],
            'ot1': scores[4], 'ot2': scores[5],
            'final': game_data['visitor_final']
        }
    elif len(scores) == 14:
        home_row = {
            'date': game_data['date'], 'visitor': game_data['visitor'], 'home': game_data['home'],
            'team': 1, 'q1': scores[7], 'q2': scores[8], 'q3': scores[9], 'q4': scores[10],
            'ot1': scores[11], 'ot2': scores[12], 'ot3': scores[13],
            'final': game_data['home_final']
        }
        visitor_row = {
            'date': game_data['date'], 'visitor': game_data['visitor'], 'home': game_data['home'],
            'team': 0, 'q1': scores[0], 'q2': scores[1], 'q3': scores[2], 'q4': scores[3],
            'ot1': scores[4], 'ot2': scores[5], 'ot3': scores[6],
            'final': game_data['visitor_final']
        }
    else:
        home_row = {
            'date': game_data['date'], 'visitor': game_data['visitor'], 'home': game_data['home'],
            'team': 1, 'q1': scores[8], 'q2': scores[9], 'q3': scores[10], 'q4': scores[11],
            'ot1': scores[12], 'ot2': scores[13], 'ot3': scores[14], 'ot4': scores[15],
            'final': game_data['home_final']
        }
        visitor_row = {
            'date': game_data['date'], 'visitor': game_data['visitor'], 'home': game_data['home'],
            'team': 0, 'q1': scores[0], 'q2': scores[1], 'q3': scores[2], 'q4': scores[3],
            'ot1': scores[4], 'ot2': scores[5], 'ot3': scores[6], 'ot4': scores[7],
            'final': game_data['visitor_final']
        }

    rows = [home_row, visitor_row]
    rows = pd.DataFrame(rows)
    game_df = pd.concat([game_df, rows], axis=0, ignore_index=True)

    return game_df


def scrape_month(season, month, latest_date, current_date):
    # Print month
    print("\t" + month)

    # Connect to website
    url = f"https://www.basketball-reference.com/leagues/NBA_{season}_games-{month}.html"
    html = urlopen(url)
    soup = BeautifulSoup(html, features="lxml")

    # Initialize dataframe
    month_df = pd.DataFrame()

    # Find games and iterate to find scoring data
    games = soup.find("table").find_all("tr")[1:]
    for game in games:
        row_data = game.find_all(["th", "td"])
        if len(row_data) > 1:
            # Print game info
            game_data = {
                'date': row_data[0].text, 
                'visitor': row_data[2].text, 'home': row_data[4].text, 
                'home_final': row_data[5].text,'visitor_final': row_data[3].text
            }
            print(f"\t\t{game_data['date']}, {game_data['visitor']} @ {game_data['home']}")

            # Check if game date is between latest date and current date
            game_date = pd.to_datetime(game_data['date'])
            game_date = date(game_date.year, game_date.month, game_date.day)

            if latest_date <= game_date < current_date:
                link = row_data[6].a["href"]
                game_df = scrape_game(link, game_data)
                month_df = pd.concat([month_df, game_df], axis=0, ignore_index=True)
            elif game_date > current_date:
                return month_df

    return month_df


def scrape_season(season, months, latest_date, current_date):
    # Print season
    print(season)
    
    # Initialize dataframe
    season_df = pd.DataFrame()

    for month in months:
        month_df = scrape_month(season + 1, month, latest_date, current_date)
        season_df = pd.concat([season_df, month_df], axis=0, ignore_index=True)

    # Append season to dataframe
    season_df['season'] = season

    return season_df


def update():
    # Load data
    df = pd.read_csv('backend/data/scoring.csv')

    # Extract latest date
    dates = pd.to_datetime(df['date'])
    latest_date = dates.max()
    latest_date = date(latest_date.year, latest_date.month, latest_date.day)

    # Current date to update until
    current_date = date.today()

    # Season and months to scrape
    season = 2022
    months = ["october", "november", "december", "january", "february", "march"]

    season_df = scrape_season(season, months, latest_date, current_date)
    df = pd.concat([df, season_df], axis=0, ignore_index=True)
    
    df = df.drop_duplicates(['date', 'visitor', 'home', 'team'], keep='last')
    df.to_csv('backend/data/scoring.csv', index=False)

