from bs4 import BeautifulSoup
from urllib.request import urlopen
import pandas as pd


def scrape_game(link, meta_data):
    # Connect to website
    url = "https://www.basketball-reference.com{}".format(link)
    html = urlopen(url)
    soup = BeautifulSoup(html, features="lxml")

    # Players dataframe
    players_df = pd.DataFrame(
        columns=['date', 'visitor', 'home', 'team', 'starter', 'player', 'mp', 'ts_perc', 'efg_perc', '3par', 'ftr',
                 'orb_perc', 'drb_perc', 'trb_perc', 'ast_perc', 'stl_perc', 'blk_perc', 'tov_perc', 'usg_perc', 'ortg',
                 'drtg', 'bpm'])

    # Home: 1, Visitor: 0
    team = 0

    # Find advanced details table and return advanced stats for each player
    tables = soup.find_all('table')
    advanced_tables = [tables[7], tables[15]]
    for table in advanced_tables:
        # Starter: 1, Bench: 0
        starter = 1

        players = table.find('tbody').find_all('tr')
        for player in players:
            if player == players[5]:
                starter = 0
            else:
                player_tags = player.find_all(['th', 'td'])
                player_data = [td.text for td in player_tags]
                if len(player_data) < 17:
                    row = {'date': meta_data['date'], 'visitor': meta_data['visitor'], 'home': meta_data['home'],
                           'team': team, 'starter': starter, 'player': player_data[0], 'mp': 0,
                           'ts_perc': 0, 'efg_perc': 0, '3par': 0, 'ftr': 0,
                           'orb_perc': 0, 'drb_perc': 0, 'trb_perc': 0, 'ast_perc': 0,
                           'stl_perc': 0, 'blk_perc': 0, 'tov_perc': 0, 'usg_perc': 0, 'ortg': 0,
                           'drtg': 0, 'bpm': 0}
                else:
                    row = {'date': meta_data['date'], 'visitor': meta_data['visitor'], 'home': meta_data['home'],
                           'team': team, 'starter': starter, 'player': player_data[0], 'mp': player_data[1],
                           'ts_perc': player_data[2], 'efg_perc': player_data[3], '3par': player_data[4],
                           'ftr': player_data[5], 'orb_perc': player_data[6], 'drb_perc': player_data[7],
                           'trb_perc': player_data[8], 'ast_perc': player_data[9], 'stl_perc': player_data[10],
                           'blk_perc': player_data[11], 'tov_perc': player_data[12], 'usg_perc': player_data[13],
                           'ortg': player_data[14], 'drtg': player_data[15], 'bpm': player_data[16]}
                players_df = players_df.append(row, ignore_index=True)

        team = 1

    return players_df


def scrape_month(season, month):
    print("\t" + month)
    # Connect to website
    url = "https://www.basketball-reference.com/leagues/NBA_{}_games-{}.html".format(str(season), month)
    html = urlopen(url)
    soup = BeautifulSoup(html, features="lxml")

    # Month dataframe
    month_df = pd.DataFrame(
        columns=['date', 'visitor', 'home', 'team', 'starter', 'player', 'mp', 'ts_perc', 'efg_perc', '3par', 'ftr',
                 'orb_perc', 'drb_perc', 'trb_perc', 'ast_perc', 'stl_perc', 'blk_perc', 'tov_perc', 'usg_perc', 'ortg',
                 'drtg', 'bpm'])

    # Find games and iterate to find scoring data
    games = soup.find("table").find_all("tr")[1:]
    for game in games:
        row_data = game.find_all(["th", "td"])
        if len(row_data) > 1:
            print("\t\t" + str(row_data[0].text) + ", " + row_data[2].text + " @ " + row_data[4].text)
            game_data = {'date': row_data[0].text, 'visitor': row_data[2].text, 'home': row_data[4].text}
            link = row_data[6].a["href"]
            month_df = month_df.append(scrape_game(link, game_data), ignore_index=True)

    return month_df


def scrape_season(season, months):
    print(season)
    # Season dataframe
    season_df = pd.DataFrame(
        columns=['date', 'visitor', 'home', 'team', 'starter', 'player', 'mp', 'ts_perc', 'efg_perc', '3par', 'ftr',
                 'orb_perc', 'drb_perc', 'trb_perc', 'ast_perc', 'stl_perc', 'blk_perc', 'tov_perc', 'usg_perc', 'ortg',
                 'drtg', 'bpm'])

    for month in months:
        season_df = season_df.append(scrape_month(season + 1, month), ignore_index=True)

    return season_df


def main():
    df = pd.DataFrame(
        columns=['date', 'visitor', 'home', 'team', 'starter', 'player', 'mp', 'ts_perc', 'efg_perc', '3par', 'ftr',
                 'orb_perc', 'drb_perc', 'trb_perc', 'ast_perc', 'stl_perc', 'blk_perc', 'tov_perc', 'usg_perc', 'ortg',
                 'drtg', 'bpm'])

    seasons = list(range(2006, 2021))
    months = ["october", "november", "december", "january", "february", "march", "april", "may", "june"]
    holdout_months = ["december", "january", "february", "march", "april", "may", "june"]
    covid_months = [["october-2019", "november", "december", "january", "february",
                     "march", "july", "august", "september", "october-2020"],
                    ["december", "january", "february", "march", "april", "may", "june", "july"]]
    for season in seasons:
        if season == 2011:
            df = df.append(scrape_season(season, holdout_months), ignore_index=True)
        elif season == 2019:
            df = df.append(scrape_season(season, covid_months[0]), ignore_index=True)
        elif season == 2020:
            df = df.append(scrape_season(season, covid_months[1]), ignore_index=True)
        else:
            df = df.append(scrape_season(season, months), ignore_index=True)

        df.to_csv('backend/data/advanced_game_details.csv')


if __name__ == '__main__':
    main()
