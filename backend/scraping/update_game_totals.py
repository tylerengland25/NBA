from bs4 import BeautifulSoup
from urllib.request import urlopen
import pandas as pd
from datetime import date


def scrape_game(link, meta_data):
    # Initialize dataframe
    totals_df = pd.DataFrame()

    # Connect to website
    url = f"https://www.basketball-reference.com{link}"
    html = urlopen(url)
    soup = BeautifulSoup(html, features="lxml")

    # Home: 1, Visitor: 0
    team = False

    # Find players table and return player stats for each team
    rows = []
    tables = soup.find_all('table')
    basic_tables = []
    for table in tables:
        if " ".join(table['id'].split('-')[-2:]) == "game basic":
            basic_tables.append(table)
    
    for table in basic_tables:
        # Data for game totals
        totals_tag = table.find_all('tr')[-1].find_all('td')
        totals = [td.text for td in totals_tag]
        team_totals = {
            'date': meta_data['date'], 'visitor': meta_data['visitor'], 'home': meta_data['home'],
            'team': int(team), 'ts_perc': totals[1], 'efg_perc': totals[2], '3par': totals[3],
            'ftr': totals[4], 'orb_perc': totals[5], 'drb_perc': totals[6], 'trb_perc': totals[7],
            'ast_perc': totals[8], 'stl_perc': totals[9], 'blk_perc': totals[10], 'tov_perc': totals[11],
            'usg_perc': totals[12], 'ortg': totals[13], 'drtg': totals[14]
            }
        
        rows.append(team_totals)

        team = not team
    rows = pd.DataFrame(rows)
    totals_df = pd.concat([totals_df, rows], axis=0, ignore_index=True)

    return totals_df


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

    # Scrape data for each month
    for month in months:
        month_df = scrape_month(season + 1, month, latest_date, current_date)
        season_df = pd.concat([season_df, month_df], axis=0, ignore_index=True)

    # Append season to dataframe
    season_df['season'] = season

    return season_df


def update():
    # Load data
    df = pd.read_csv(f'backend/data/totals/game_totals.csv')

    # Extract latest date
    dates = pd.to_datetime(df.loc[:, 'date'])
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
    df.to_csv('backend/data/totals/game_totals.csv', index=False)
