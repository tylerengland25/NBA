from bs4 import BeautifulSoup
from urllib.request import urlopen
import pandas as pd


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

    seasons = [2006]
    months = ["october"]
    for season in seasons:

        season_df = scrape_season(season, months)
        for key in df:
            df[key] = df[key].append(season_df[key], ignore_index=True)
            df[key].to_csv('backend/data/' + key + '.csv')


if __name__ == '__main__':
    main()