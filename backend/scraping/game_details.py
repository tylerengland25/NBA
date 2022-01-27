from bs4 import BeautifulSoup
from urllib.request import urlopen
import pandas as pd


def scrape_game(link, meta_data):
    # Different types of game_details labels
    game_details_label = {0: '', 1: '_q1', 2: '_q2', 3: '_h1', 4: '_q3', 5: '_q4', 6: '_h2',
                          7: '_ot1', 8: '_ot2', 9: '_ot3', 10: '_ot4', 'advanced': None}

    # Different types of season dataframes
    players_df = {}
    for key in game_details_label:
        if game_details_label[key] is None:
            players_df['advanced_details'] = pd.DataFrame(
                columns=['date', 'visitor', 'home', 'team', 'starter', 'player', 'mp', 'ts_perc', 'efg_perc', '3par',
                         'ftr', 'orb_perc', 'drb_perc', 'trb_perc', 'ast_perc', 'stl_perc', 'blk_perc', 'tov_perc',
                         'usg_perc', 'ortg', 'drtg', 'bpm'])
        else:
            players_df['game_details' + game_details_label[key]] = pd.DataFrame(
                columns=['date', 'visitor', 'home', 'team', 'starter', 'player', 'mp', 'fg', 'fga', 'fg_perc',
                         '3p', '3pa', '3p_perc', 'ft', 'fta', 'ft_perc', 'orb', 'drb', 'trb', 'ast', 'stl', 'blk',
                         'tov', 'pf', 'pts', 'plus_minus'])

    # Connect to website
    url = "https://www.basketball-reference.com{}".format(link)
    html = urlopen(url)
    soup = BeautifulSoup(html, features="lxml")

    # Find players table and return player stats for each team
    label = 0
    tables = soup.find_all('table')
    for table in tables:

        # Which file to append dataframe to
        if label == len(tables)/2 - 1:
            filename = 'advanced_details'
            label = -1
        else:
            filename = 'game_details' + game_details_label[label]

        # Home: 1, Visitor: 0
        team = 0 if label < len(tables)/2 else 1

        # Starter: 1, Bench: 0
        starter = 1

        # Data for each player
        players = table.find('tbody').find_all('tr')
        for player in players:
            if player == players[5]:
                starter = 0
            else:
                player_tags = player.find_all(['th', 'td'])
                player_data = [td.text for td in player_tags]
                if len(player_data) < 21 and filename != 'advanced_details':
                    row = {'date': meta_data['date'], 'visitor': meta_data['visitor'], 'home': meta_data['home'],
                           'team': team, 'starter': starter, 'player': player_data[0], 'mp': 0,
                           'fg': 0, 'fga': 0, 'fg_perc': 0, '3p': 0, '3pa': 0, '3p_perc': 0,
                           'ft': 0, 'fta': 0, 'ft_perc': 0, 'orb': 0, 'drb': 0, 'trb': 0,
                           'ast': 0, 'stl': 0, 'blk': 0, 'tov': 0, 'pf': 0, 'pts': 0, 'plus_minus': 0}
                elif filename != 'advanced_details':
                    row = {'date': meta_data['date'], 'visitor': meta_data['visitor'], 'home': meta_data['home'],
                           'team': team, 'starter': starter, 'player': player_data[0], 'mp': player_data[1],
                           'fg': player_data[2], 'fga': player_data[3], 'fg_perc': player_data[4],
                           '3p': player_data[5], '3pa': player_data[6], '3p_perc': player_data[7],
                           'ft': player_data[8], 'fta': player_data[9], 'ft_perc': player_data[10],
                           'orb': player_data[11], 'drb': player_data[12], 'trb': player_data[13],
                           'ast': player_data[14], 'stl': player_data[15], 'blk': player_data[16],
                           'tov': player_data[17], 'pf': player_data[18], 'pts': player_data[19],
                           'plus_minus': player_data[20]}
                elif len(player_data) < 17 and filename == 'advanced_details':
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
                players_df[filename] = players_df[filename].append(row, ignore_index=True)

        label += 1

    return players_df


def scrape_month(season, month):
    print("\t" + month)
    # Connect to website
    url = "https://www.basketball-reference.com/leagues/NBA_{}_games-{}.html".format(str(season), month)
    html = urlopen(url)
    soup = BeautifulSoup(html, features="lxml")

    # Different types of game_details labels
    game_details_label = {0: '', 1: '_q1', 2: '_q2', 3: '_h1', 4: '_q3', 5: '_q4', 6: '_h2',
                          7: '_ot1', 8: '_ot2', 9: '_ot3', 10: '_ot4', 'advanced': None}

    # Different types of season dataframes
    month_df = {}
    for key in game_details_label:
        if game_details_label[key] is None:
            month_df['advanced_details'] = pd.DataFrame(
                columns=['date', 'visitor', 'home', 'team', 'starter', 'player', 'mp', 'ts_perc', 'efg_perc', '3par',
                         'ftr', 'orb_perc', 'drb_perc', 'trb_perc', 'ast_perc', 'stl_perc', 'blk_perc', 'tov_perc',
                         'usg_perc', 'ortg', 'drtg', 'bpm'])
        else:
            month_df['game_details' + game_details_label[key]] = pd.DataFrame(
                columns=['date', 'visitor', 'home', 'team', 'starter', 'player', 'mp', 'fg', 'fga', 'fg_perc',
                         '3p', '3pa', '3p_perc', 'ft', 'fta', 'ft_perc', 'orb', 'drb', 'trb', 'ast', 'stl', 'blk',
                         'tov', 'pf', 'pts', 'plus_minus'])

    # Find games and iterate to find scoring data
    games = soup.find("table").find_all("tr")[1:]
    for game in games:
        row_data = game.find_all(["th", "td"])
        if len(row_data) > 1:
            print("\t\t" + str(row_data[0].text) + ", " + row_data[2].text + " @ " + row_data[4].text)
            game_data = {'date': row_data[0].text, 'visitor': row_data[2].text, 'home': row_data[4].text}
            link = row_data[6].a["href"]
            players_df = scrape_game(link, game_data)
            for key in month_df:
                month_df[key] = month_df[key].append(players_df[key], ignore_index=True)

    return month_df


def scrape_season(season, months):
    print(season)
    # Different types of game_details labels
    game_details_label = {0: '', 1: '_q1', 2: '_q2', 3: '_h1', 4: '_q3', 5: '_q4', 6: '_h2',
                          7: '_ot1', 8: '_ot2', 9: '_ot3', 10: '_ot4', 'advanced': None}

    # Different types of season dataframes
    season_df = {}
    for key in game_details_label:
        if game_details_label[key] is None:
            season_df['advanced_details'] = pd.DataFrame(
                columns=['date', 'visitor', 'home', 'team', 'starter', 'player', 'mp', 'ts_perc', 'efg_perc', '3par',
                         'ftr', 'orb_perc', 'drb_perc', 'trb_perc', 'ast_perc', 'stl_perc', 'blk_perc', 'tov_perc',
                         'usg_perc', 'ortg', 'drtg', 'bpm'])
        else:
            season_df['game_details' + game_details_label[key]] = pd.DataFrame(
                columns=['date', 'visitor', 'home', 'team', 'starter', 'player', 'mp', 'fg', 'fga', 'fg_perc',
                         '3p', '3pa', '3p_perc', 'ft', 'fta', 'ft_perc', 'orb', 'drb', 'trb', 'ast', 'stl', 'blk',
                         'tov', 'pf', 'pts', 'plus_minus'])

    for month in months:
        month_df = scrape_month(season + 1, month)
        for key in season_df:
            season_df[key] = season_df[key].append(month_df[key], ignore_index=True)

    return season_df


def main():
    # Different types of game_details labels
    game_details_label = {0: '', 1: '_q1', 2: '_q2', 3: '_h1', 4: '_q3', 5: '_q4', 6: '_h2',
                          7: '_ot1', 8: '_ot2', 9: '_ot3', 10: '_ot4', 'advanced': None}

    # Different types of season dataframes
    df = {}
    for key in game_details_label:
        if game_details_label[key] is None:
            df['advanced_details'] = pd.DataFrame(
                columns=['date', 'visitor', 'home', 'team', 'starter', 'player', 'mp', 'ts_perc', 'efg_perc', '3par',
                         'ftr', 'orb_perc', 'drb_perc', 'trb_perc', 'ast_perc', 'stl_perc', 'blk_perc', 'tov_perc',
                         'usg_perc', 'ortg', 'drtg', 'bpm'])
        else:
            df['game_details' + game_details_label[key]] = pd.DataFrame(
                columns=['date', 'visitor', 'home', 'team', 'starter', 'player', 'mp', 'fg', 'fga', 'fg_perc',
                         '3p', '3pa', '3p_perc', 'ft', 'fta', 'ft_perc', 'orb', 'drb', 'trb', 'ast', 'stl', 'blk',
                         'tov', 'pf', 'pts', 'plus_minus'])

    seasons = [2018]
    months = ["may"]
    holdout_months = ["december", "january", "february", "march", "april", "may", "june"]
    covid_months = [["october-2019", "november", "december", "january", "february",
                     "march", "july", "august", "september", "october-2020"],
                    ["december", "january", "february", "march", "april", "may", "june", "july"]]
    for season in seasons:
        if season == 2011:
            season_months = holdout_months
        elif season == 2019:
            season_months = covid_months[0]
        elif season == 2020:
            season_months = covid_months[1]
        else:
            season_months = months

        season_df = scrape_season(season, season_months)
        for key in df:
            df[key] = df[key].append(season_df[key], ignore_index=True)
            df[key].to_csv('backend/data/' + key + '.csv')


if __name__ == '__main__':
    main()
