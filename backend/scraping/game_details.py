from bs4 import BeautifulSoup
from urllib.request import urlopen
import pandas as pd


def scrape_game(link, meta_data):
    # Different types of game_details labels
    game_details_label = {0: '', 1: '_q1', 2: '_q2', 3: '_h1', 4: '_q3', 5: '_q4', 6: '_h2', 7: None,
                          8: '', 9: '_q1', 10: '_q2', 11: '_h1', 12: '_q3', 13: '_q4', 14: '_h2', 15: None}
    label = 0

    # Different types of player dataframes
    players_df = {}
    for key in game_details_label:
        if game_details_label[key] is None:
            pass
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
    tables = soup.find_all('table')
    for table in tables:
        if game_details_label.get(label) is None:
            pass
        else:
            # Home: 1, Visitor: 0
            team = 0 if label < 8 else 1

            # Which file to append dataframe to
            filename = 'game_details' + game_details_label[label]

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
                    if len(player_data) < 21:
                        row = {'date': meta_data['date'], 'visitor': meta_data['visitor'], 'home': meta_data['home'],
                               'team': team, 'starter': starter, 'player': player_data[0], 'mp': 0,
                               'fg': 0, 'fga': 0, 'fg_perc': 0, '3p': 0, '3pa': 0, '3p_perc': 0,
                               'ft': 0, 'fta': 0, 'ft_perc': 0, 'orb': 0, 'drb': 0, 'trb': 0,
                               'ast': 0, 'stl': 0, 'blk': 0, 'tov': 0, 'pf': 0, 'pts': 0, 'plus_minus': 0}
                    else:
                        row = {'date': meta_data['date'], 'visitor': meta_data['visitor'], 'home': meta_data['home'],
                               'team': team, 'starter': starter, 'player': player_data[0], 'mp': player_data[1],
                               'fg': player_data[2], 'fga': player_data[3], 'fg_perc': player_data[4],
                               '3p': player_data[5], '3pa': player_data[6], '3p_perc': player_data[7],
                               'ft': player_data[8], 'fta': player_data[9], 'ft_perc': player_data[10],
                               'orb': player_data[11], 'drb': player_data[12], 'trb': player_data[13],
                               'ast': player_data[14], 'stl': player_data[15], 'blk': player_data[16],
                               'tov': player_data[17], 'pf': player_data[18], 'pts': player_data[19],
                               'plus_minus': player_data[20]}
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
    game_details_label = {0: '', 1: '_q1', 2: '_q2', 3: '_h1', 4: '_q3', 5: '_q4', 6: '_h2', 7: None,
                          8: '', 9: '_q1', 10: '_q2', 11: '_h1', 12: '_q3', 13: '_q4', 14: '_h2', 15: None}

    # Different types of month dataframes
    month_df = {}
    for key in game_details_label:
        if game_details_label[key] is None:
            pass
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
    game_details_label = {0: '', 1: '_q1', 2: '_q2', 3: '_h1', 4: '_q3', 5: '_q4', 6: '_h2', 7: None,
                          8: '', 9: '_q1', 10: '_q2', 11: '_h1', 12: '_q3', 13: '_q4', 14: '_h2', 15: None}

    # Different types of season dataframes
    season_df = {}
    for key in game_details_label:
        if game_details_label[key] is None:
            pass
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
    game_details_label = {0: '', 1: '_q1', 2: '_q2', 3: '_h1', 4: '_q3', 5: '_q4', 6: '_h2', 7: None,
                          8: '', 9: '_q1', 10: '_q2', 11: '_h1', 12: '_q3', 13: '_q4', 14: '_h2', 15: None}

    # Different types of season dataframes
    df = {}
    for key in game_details_label:
        if game_details_label[key] is None:
            pass
        else:
            df['game_details' + game_details_label[key]] = pd.DataFrame(
                columns=['date', 'visitor', 'home', 'team', 'starter', 'player', 'mp', 'fg', 'fga', 'fg_perc',
                         '3p', '3pa', '3p_perc', 'ft', 'fta', 'ft_perc', 'orb', 'drb', 'trb', 'ast', 'stl', 'blk',
                         'tov', 'pf', 'pts', 'plus_minus'])

    seasons = list(range(2006, 2021))
    months = ["october", "november", "december", "january", "february", "march", "april", "may", "june"]
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
