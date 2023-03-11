from bs4 import BeautifulSoup
from urllib.request import urlopen
import pandas as pd
from datetime import date


def scrape_game(link, meta_data):
    # Initialize dataframe
    players_df = pd.DataFrame()

    # Connect to website
    url = f"https://www.basketball-reference.com{link}"
    html = urlopen(url)
    soup = BeautifulSoup(html, features="lxml")

    # Home: 1, Visitor: 0
    team = False

    # Find players table and return player stats for each team
    basic_tables = []
    tables = soup.find_all('table')
    for table in tables:
        if " ".join(table['id'].split('-')[-2:]) == "game basic":
            basic_tables.append(table)
    
    for table in basic_tables:
        # Starter: 1, Bench: 0
        starter = 1

        # Data for player details
        players = table.find('tbody').find_all('tr')
        rows = []
        for player in players:
            if player == players[5]:
                starter = 0
            else:
                player_tags = player.find_all(['th', 'td'])
                player_data = [td.text for td in player_tags]
                if len(player_data) < 21:
                    row = {
                        'date': meta_data['date'], 'visitor': meta_data['visitor'], 'home': meta_data['home'],
                        'team': int(team), 'starter': starter, 'player': player_data[0], 'mp': 0,
                        'fg': 0, 'fga': 0, 'fg_perc': 0, '3p': 0, '3pa': 0, '3p_perc': 0,
                        'ft': 0, 'fta': 0, 'ft_perc': 0, 'orb': 0, 'drb': 0, 'trb': 0,
                        'ast': 0, 'stl': 0, 'blk': 0, 'tov': 0, 'pf': 0, 'pts': 0, 'plus_minus': 0
                    }
                else:
                    row = {
                        'date': meta_data['date'], 'visitor': meta_data['visitor'], 'home': meta_data['home'],
                        'team': int(team), 'starter': starter, 'player': player_data[0], 'mp': player_data[1],
                        'fg': player_data[2], 'fga': player_data[3], 'fg_perc': player_data[4],
                        '3p': player_data[5], '3pa': player_data[6], '3p_perc': player_data[7],
                        'ft': player_data[8], 'fta': player_data[9], 'ft_perc': player_data[10],
                        'orb': player_data[11], 'drb': player_data[12], 'trb': player_data[13],
                        'ast': player_data[14], 'stl': player_data[15], 'blk': player_data[16],
                        'tov': player_data[17], 'pf': player_data[18], 'pts': player_data[19],
                        'plus_minus': player_data[20]
                    }
                rows.append(row)
        rows = pd.DataFrame(rows)
        players_df = pd.concat([players_df, rows], axis=0, ignore_index=True)

        team = not team
        
    return players_df


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
    df = pd.read_csv(f'backend/data/details/game_details.csv')

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

    df = df.drop_duplicates(['date', 'visitor', 'home', 'team', 'player'], keep='last')
    df.to_csv('backend/data/details/game_details.csv', index=False)
