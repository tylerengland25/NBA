from bs4 import BeautifulSoup
from urllib.request import urlopen
import pandas as pd
from datetime import date


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

    # Different types of game_total labels
    game_totals_label = {0: 'game', 1: 'q1', 2: 'q2', 3: 'h1', 4: 'q3', 5: 'q4', 6: 'h2',
                         7: 'ot1', 8: 'ot2', 9: 'ot3', 10: 'ot4', 'advanced': None}

    for key in game_totals_label:
        if game_totals_label[key] is None:
            players_df['advanced_totals'] = pd.DataFrame(
                columns=['date', 'visitor', 'home', 'team', 'ts_perc', 'efg_perc', '3par', 'ftr', 'orb_perc',
                         'drb_perc', 'trb_perc', 'ast_perc', 'stl_perc', 'blk_perc', 'tov_perc', 'usg_perc',
                         'ortg', 'drtg'])
        else:
            players_df[game_totals_label[key] + '_totals'] = pd.DataFrame(
                columns=['date', 'visitor', 'home', 'team', 'fg', 'fga', 'fg_perc', '3p', '3pa', '3p_perc',
                         'ft', 'fta', 'ft_perc', 'orb', 'drb', 'trb', 'ast', 'stl', 'blk', 'tov', 'pf', 'pts'])

    # Connect to website
    url = "https://www.basketball-reference.com{}".format(link)
    html = urlopen(url)
    soup = BeautifulSoup(html, features="lxml")

    # Home: 1, Visitor: 0
    team = False

    # Find players table and return player stats for each team
    label = 0
    tables = soup.find_all('table')
    for table in tables:

        # Which file to append dataframe to
        if label == len(tables) / 2 - 1:
            detail_filename = 'advanced_details'
            total_filename = 'advanced_totals'
            label = -1
        else:
            detail_filename = 'game_details' + game_details_label[label]
            total_filename = game_totals_label[label] + '_totals'

        # Starter: 1, Bench: 0
        starter = 1

        # Data for player details
        players = table.find('tbody').find_all('tr')
        for player in players:
            if player == players[5]:
                starter = 0
            else:
                player_tags = player.find_all(['th', 'td'])
                player_data = [td.text for td in player_tags]
                if len(player_data) < 21 and detail_filename != 'advanced_details':
                    row = {'date': meta_data['date'], 'visitor': meta_data['visitor'], 'home': meta_data['home'],
                           'team': int(team), 'starter': starter, 'player': player_data[0], 'mp': 0,
                           'fg': 0, 'fga': 0, 'fg_perc': 0, '3p': 0, '3pa': 0, '3p_perc': 0,
                           'ft': 0, 'fta': 0, 'ft_perc': 0, 'orb': 0, 'drb': 0, 'trb': 0,
                           'ast': 0, 'stl': 0, 'blk': 0, 'tov': 0, 'pf': 0, 'pts': 0, 'plus_minus': 0}
                elif detail_filename != 'advanced_details':
                    row = {'date': meta_data['date'], 'visitor': meta_data['visitor'], 'home': meta_data['home'],
                           'team': int(team), 'starter': starter, 'player': player_data[0], 'mp': player_data[1],
                           'fg': player_data[2], 'fga': player_data[3], 'fg_perc': player_data[4],
                           '3p': player_data[5], '3pa': player_data[6], '3p_perc': player_data[7],
                           'ft': player_data[8], 'fta': player_data[9], 'ft_perc': player_data[10],
                           'orb': player_data[11], 'drb': player_data[12], 'trb': player_data[13],
                           'ast': player_data[14], 'stl': player_data[15], 'blk': player_data[16],
                           'tov': player_data[17], 'pf': player_data[18], 'pts': player_data[19],
                           'plus_minus': player_data[20]}
                elif len(player_data) < 17 and detail_filename == 'advanced_details':
                    row = {'date': meta_data['date'], 'visitor': meta_data['visitor'], 'home': meta_data['home'],
                           'team': int(team), 'starter': starter, 'player': player_data[0], 'mp': 0,
                           'ts_perc': 0, 'efg_perc': 0, '3par': 0, 'ftr': 0,
                           'orb_perc': 0, 'drb_perc': 0, 'trb_perc': 0, 'ast_perc': 0,
                           'stl_perc': 0, 'blk_perc': 0, 'tov_perc': 0, 'usg_perc': 0, 'ortg': 0,
                           'drtg': 0, 'bpm': 0}
                else:
                    row = {'date': meta_data['date'], 'visitor': meta_data['visitor'], 'home': meta_data['home'],
                           'team': int(team), 'starter': starter, 'player': player_data[0], 'mp': player_data[1],
                           'ts_perc': player_data[2], 'efg_perc': player_data[3], '3par': player_data[4],
                           'ftr': player_data[5], 'orb_perc': player_data[6], 'drb_perc': player_data[7],
                           'trb_perc': player_data[8], 'ast_perc': player_data[9], 'stl_perc': player_data[10],
                           'blk_perc': player_data[11], 'tov_perc': player_data[12], 'usg_perc': player_data[13],
                           'ortg': player_data[14], 'drtg': player_data[15], 'bpm': player_data[16]}
                players_df[detail_filename] = players_df[detail_filename].append(row, ignore_index=True)

        # Data for game totals
        totals_tag = table.find_all('tr')[-1].find_all('td')
        totals = [td.text for td in totals_tag]
        if total_filename != 'advanced_totals':
            team_totals = {'date': meta_data['date'], 'visitor': meta_data['visitor'], 'home': meta_data['home'],
                           'team': int(team), 'fg': totals[1], 'fga': totals[2], 'fg_perc': totals[3], '3p': totals[4],
                           '3pa': totals[5], '3p_perc': totals[6], 'ft': totals[7], 'fta': totals[8],
                           'ft_perc': totals[9], 'orb': totals[10], 'drb': totals[11], 'trb': totals[12],
                           'ast': totals[13], 'stl': totals[14], 'blk': totals[15], 'tov': totals[16], 'pf': totals[17],
                           'pts': totals[18]}
        else:
            team_totals = {'date': meta_data['date'], 'visitor': meta_data['visitor'], 'home': meta_data['home'],
                           'team': int(team), 'ts_perc': totals[1], 'efg_perc': totals[2], '3par': totals[3],
                           'ftr': totals[4], 'orb_perc': totals[5], 'drb_perc': totals[6], 'trb_perc': totals[7],
                           'ast_perc': totals[8], 'stl_perc': totals[9], 'blk_perc': totals[10], 'tov_perc': totals[11],
                           'usg_perc': totals[12], 'ortg': totals[13], 'drtg': totals[14]}
        players_df[total_filename] = players_df[total_filename].append(team_totals, ignore_index=True)

        if label == -1:
            team = not team
        label += 1

    return players_df


def scrape_month(season, month, latest_date, current_date):
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

    # Different types of game_total labels
    game_totals_label = {0: 'game', 1: 'q1', 2: 'q2', 3: 'h1', 4: 'q3', 5: 'q4', 6: 'h2',
                         7: 'ot1', 8: 'ot2', 9: 'ot3', 10: 'ot4', 'advanced': None}

    for key in game_totals_label:
        if game_totals_label[key] is None:
            month_df['advanced_totals'] = pd.DataFrame(
                columns=['date', 'visitor', 'home', 'team', 'ts_perc', 'efg_perc', '3par', 'ftr', 'orb_perc',
                         'drb_perc', 'trb_perc', 'ast_perc', 'stl_perc', 'blk_perc', 'tov_perc', 'usg_perc',
                         'ortg', 'drtg'])
        else:
            month_df[game_totals_label[key] + '_totals'] = pd.DataFrame(
                columns=['date', 'visitor', 'home', 'team', 'fg', 'fga', 'fg_perc', '3p', '3pa', '3p_perc',
                         'ft', 'fta', 'ft_perc', 'orb', 'drb', 'trb', 'ast', 'stl', 'blk', 'tov', 'pf', 'pts'])

    # Find games and iterate to find scoring data
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
                players_df = scrape_game(link, game_data)
                for key in month_df:
                    month_df[key] = month_df[key].append(players_df[key], ignore_index=True)
            elif game_date == current_date:
                for key in month_df:
                    month_df[key] = month_df[key].append(
                        {'date': game_data['date'], 'visitor': game_data['visitor'],
                         'home': game_data['home'], 'team': 1, 'starter': 1
                         },
                        ignore_index=True
                    )
                    month_df[key] = month_df[key].append(
                        {'date': game_data['date'], 'visitor': game_data['visitor'],
                         'home': game_data['home'], 'team': 1, 'starter': 0
                         },
                        ignore_index=True
                    )
                    month_df[key] = month_df[key].append(
                        {'date': game_data['date'], 'visitor': game_data['visitor'],
                         'home': game_data['home'], 'team': 0, 'starter': 1
                         },
                        ignore_index=True
                    )
                    month_df[key] = month_df[key].append(
                        {'date': game_data['date'], 'visitor': game_data['visitor'],
                         'home': game_data['home'], 'team': 0, 'starter': 0
                         },
                        ignore_index=True
                    )
            elif game_date > current_date:
                return month_df

    return month_df


def scrape_season(season, months, latest_date, current_date):
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

    # Different types of game_total labels
    game_totals_label = {0: 'game', 1: 'q1', 2: 'q2', 3: 'h1', 4: 'q3', 5: 'q4', 6: 'h2',
                         7: 'ot1', 8: 'ot2', 9: 'ot3', 10: 'ot4', 'advanced': None}

    for key in game_totals_label:
        if game_totals_label[key] is None:
            season_df['advanced_totals'] = pd.DataFrame(
                columns=['date', 'visitor', 'home', 'team', 'ts_perc', 'efg_perc', '3par', 'ftr', 'orb_perc',
                         'drb_perc', 'trb_perc', 'ast_perc', 'stl_perc', 'blk_perc', 'tov_perc', 'usg_perc',
                         'ortg', 'drtg'])
        else:
            season_df[game_totals_label[key] + '_totals'] = pd.DataFrame(
                columns=['date', 'visitor', 'home', 'team', 'fg', 'fga', 'fg_perc', '3p', '3pa', '3p_perc',
                         'ft', 'fta', 'ft_perc', 'orb', 'drb', 'trb', 'ast', 'stl', 'blk', 'tov', 'pf', 'pts'])

    for month in months:
        month_df = scrape_month(season + 1, month, latest_date, current_date)
        for key in season_df:
            season_df[key] = season_df[key].append(month_df[key], ignore_index=True)

    season_df['season'] = season
    return season_df


def main():
    # Different types of game_details labels
    game_details_label = {0: '', 1: '_q1', 2: '_q2', 3: '_h1', 4: '_q3', 5: '_q4', 6: '_h2',
                          7: '_ot1', 8: '_ot2', 9: '_ot3', 10: '_ot4', 'advanced': None}

    # Different types of season dataframes
    df = {}
    for key in game_details_label:
        if game_details_label[key] is None:
            df['advanced_details'] = \
                pd.read_csv('backend/data/details/advanced_details.csv').drop(['Unnamed: 0'], axis=1)
        else:
            df['game_details' + game_details_label[key]] = \
                pd.read_csv(f'backend/data/details/game_details{game_details_label[key]}.csv').drop(
                    ['Unnamed: 0'], axis=1
                )

    # Different types of game_total labels
    game_totals_label = {0: 'game', 1: 'q1', 2: 'q2', 3: 'h1', 4: 'q3', 5: 'q4', 6: 'h2',
                         7: 'ot1', 8: 'ot2', 9: 'ot3', 10: 'ot4', 'advanced': None}

    for key in game_totals_label:
        if game_totals_label[key] is None:
            df['advanced_totals'] = \
                pd.read_csv('backend/data/totals/advanced_totals.csv').drop(['Unnamed: 0'], axis=1)
        else:
            df[game_totals_label[key] + '_totals'] = \
                pd.read_csv(f'backend/data/totals/{game_totals_label[key]}_totals.csv').drop(['Unnamed: 0'], axis=1)

    dates = pd.to_datetime(df['game_details']['date'])

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

    season_df = scrape_season(season, months, latest_date, current_date)
    for key in df:
        df[key] = df[key].append(season_df[key], ignore_index=True)

        if key.split('_')[1] == 'totals':
            df[key] = df[key].drop_duplicates(['date', 'visitor', 'home', 'team'], keep='last')
            df[key].to_csv('backend/data/totals/' + key + '.csv')
        else:
            df[key] = df[key].drop_duplicates(['date', 'visitor', 'home', 'team', 'starter', 'player'], keep='last')
            df[key].to_csv('backend/data/details/' + key + '.csv')


if __name__ == '__main__':
    main()
