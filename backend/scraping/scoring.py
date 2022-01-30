from bs4 import BeautifulSoup
from urllib.request import urlopen
import re
import pandas as pd


def scrape_game(link, game_data):
    # Connect to website
    url = "https://www.basketball-reference.com{}".format(link)
    html = urlopen(url)
    soup = BeautifulSoup(html, features="lxml")

    # Game dataframe
    game_df = pd.DataFrame(
        columns=['date', 'visitor', 'home', 'team', 'q1', 'q2', 'q3', 'q4', 'ot1', 'ot2', 'ot3', 'ot4', 'final'])

    # Find scoring table and return quarter scores for both teams
    scoring_tag = soup.find('div', attrs={'class': 'content_grid'}).find('div')
    table_data = re.findall("(?<=\>)(\d*?)(?=\</td>)", str(scoring_tag))
    scores = []
    for td in table_data:
        if len(td) > 0:
            scores.append(int(td))

    if len(scores) == 8:
        game_df = game_df.append({'date': game_data['date'], 'visitor': game_data['visitor'], 'home': game_data['home'],
                                  'team': 1, 'q1': scores[4], 'q2': scores[5], 'q3': scores[6], 'q4': scores[7],
                                  'final': game_data['home_final']},
                                 ignore_index=True)
        game_df = game_df.append({'date': game_data['date'], 'visitor': game_data['visitor'], 'home': game_data['home'],
                                  'team': 0, 'q1': scores[0], 'q2': scores[1], 'q3': scores[2], 'q4': scores[3],
                                  'final': game_data['visitor_final']},
                                 ignore_index=True)
    elif len(scores) == 10:
        game_df = game_df.append({'date': game_data['date'], 'visitor': game_data['visitor'], 'home': game_data['home'],
                                  'team': 1, 'q1': scores[5], 'q2': scores[6], 'q3': scores[7], 'q4': scores[8],
                                  'ot1': scores[9],
                                  'final': game_data['home_final']},
                                 ignore_index=True)
        game_df = game_df.append({'date': game_data['date'], 'visitor': game_data['visitor'], 'home': game_data['home'],
                                  'team': 0, 'q1': scores[0], 'q2': scores[1], 'q3': scores[2], 'q4': scores[3],
                                  'ot1': scores[4],
                                  'final': game_data['visitor_final']},
                                 ignore_index=True)
    elif len(scores) == 12:
        game_df = game_df.append({'date': game_data['date'], 'visitor': game_data['visitor'], 'home': game_data['home'],
                                  'team': 1, 'q1': scores[6], 'q2': scores[7], 'q3': scores[8], 'q4': scores[9],
                                  'ot1': scores[10], 'ot2': scores[11],
                                  'final': game_data['home_final']},
                                 ignore_index=True)
        game_df = game_df.append({'date': game_data['date'], 'visitor': game_data['visitor'], 'home': game_data['home'],
                                  'team': 0, 'q1': scores[0], 'q2': scores[1], 'q3': scores[2], 'q4': scores[3],
                                  'ot1': scores[4], 'ot2': scores[5],
                                  'final': game_data['visitor_final']},
                                 ignore_index=True)
    elif len(scores) == 14:
        game_df = game_df.append({'date': game_data['date'], 'visitor': game_data['visitor'], 'home': game_data['home'],
                                  'team': 1, 'q1': scores[7], 'q2': scores[8], 'q3': scores[9], 'q4': scores[10],
                                  'ot1': scores[11], 'ot2': scores[12], 'ot3': scores[13],
                                  'final': game_data['home_final']},
                                 ignore_index=True)
        game_df = game_df.append({'date': game_data['date'], 'visitor': game_data['visitor'], 'home': game_data['home'],
                                  'team': 0, 'q1': scores[0], 'q2': scores[1], 'q3': scores[2], 'q4': scores[3],
                                  'ot1': scores[4], 'ot2': scores[5], 'ot3': scores[6],
                                  'final': game_data['visitor_final']},
                                 ignore_index=True)
    else:
        game_df = game_df.append({'date': game_data['date'], 'visitor': game_data['visitor'], 'home': game_data['home'],
                                  'team': 1, 'q1': scores[8], 'q2': scores[9], 'q3': scores[10], 'q4': scores[11],
                                  'ot1': scores[12], 'ot2': scores[13], 'ot3': scores[14], 'ot4': scores[15],
                                  'final': game_data['home_final']},
                                 ignore_index=True)
        game_df = game_df.append({'date': game_data['date'], 'visitor': game_data['visitor'], 'home': game_data['home'],
                                  'team': 0, 'q1': scores[0], 'q2': scores[1], 'q3': scores[2], 'q4': scores[3],
                                  'ot1': scores[4], 'ot2': scores[5], 'ot3': scores[6], 'ot4': scores[7],
                                  'final': game_data['visitor_final']},
                                 ignore_index=True)

    return game_df


def scrape_month(season, month):
    print("\t" + month)
    # Connect to website
    url = "https://www.basketball-reference.com/leagues/NBA_{}_games-{}.html".format(str(season), month)
    html = urlopen(url)
    soup = BeautifulSoup(html, features="lxml")

    # Month dataframe
    month_df = pd.DataFrame(
        columns=['date', 'visitor', 'home', 'team', 'q1', 'q2', 'q3', 'q4', 'ot1', 'ot2', 'ot3', 'ot4', 'final'])

    # Find games and iterate to find scoring data
    games = soup.find("table").find_all("tr")[1:]
    for game in games:
        row_data = game.find_all(["th", "td"])
        if len(row_data) > 1:
            print("\t\t" + str(row_data[0].text) + ", " + row_data[2].text + " @ " + row_data[4].text)
            game_data = {'date': row_data[0].text,
                         'visitor': row_data[2].text, 'visitor_final': row_data[3].text,
                         'home': row_data[4].text, 'home_final': row_data[5].text}
            link = row_data[6].a["href"]
            month_df = month_df.append(scrape_game(link, game_data), ignore_index=True)

    return month_df


def scrape_season(season, months):
    print(season)
    # Season dataframe
    season_df = pd.DataFrame(
        columns=['date', 'visitor', 'home', 'team', 'q1', 'q2', 'q3', 'q4', 'ot1', 'ot2', 'ot3', 'ot4', 'final'])

    for month in months:
        season_df = season_df.append(scrape_month(season + 1, month), ignore_index=True)

    return season_df


def main():
    df = pd.DataFrame(
        columns=['date', 'visitor', 'home', 'team', 'q1', 'q2', 'q3', 'q4', 'ot1', 'ot2', 'ot3', 'ot4', 'final'])

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

        df.to_csv('backend/data/scoring.csv')


if __name__ == '__main__':
    main()
