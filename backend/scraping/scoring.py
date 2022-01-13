from bs4 import BeautifulSoup
from urllib.request import urlopen
import re
import pandas as pd


def scrape_game(link):
    # Connect to website
    url = "https://www.basketball-reference.com{}".format(link)
    html = urlopen(url)
    soup = BeautifulSoup(html, features="lxml")

    # Find scoring table and return quarter scores for both teams
    scoring_tag = soup.find('div', attrs={'class': 'content_grid'}).find('div')
    table_data = re.findall("(?<=\>)(\d*?)(?=\</td>)", str(scoring_tag))
    scores = []
    for td in table_data:
        if len(td) > 0:
            scores.append(int(td))
    scoring_data = {'visitor_q1': scores[0], 'home_q1': scores[4], 'visitor_q2': scores[1], 'home_q2': scores[5],
                    'visitor_q3': scores[2], 'home_q3': scores[6], 'visitor_q4': scores[3], 'home_q4': scores[7]}
    return scoring_data


def scrape_month(season, month):
    print("\t" + month)
    # Connect to website
    url = "https://www.basketball-reference.com/leagues/NBA_{}_games-{}.html".format(str(season), month)
    html = urlopen(url)
    soup = BeautifulSoup(html, features="lxml")

    # Month datframe
    month_df = pd.DataFrame(columns=['date', 'visitor', 'home', 'visitor_q1', 'home_q1', 'visitor_q2', 'home_q2',
                                     'visitor_q3', 'home_q3', 'visitor_q4', 'home_q4', 'visitor_final', 'home_final'])

    # Find games and iterate to find scoring data
    games = soup.find("table").find_all("tr")[1:]
    for game in games:
        row_data = game.find_all(["th", "td"])
        if len(row_data) > 1:
            print("\t\t" + str(row_data[0].text))
            game_data = {'date': row_data[0].text,
                         'visitor': row_data[2].text, 'visitor_final': row_data[3].text,
                         'home': row_data[4].text, 'home_final': row_data[5].text}
            link = row_data[6].a["href"]
            game_data.update(scrape_game(link))
            month_df = month_df.append(game_data, ignore_index=True)

    return month_df


def scrape_season(season, months):
    print(season)
    # Season dataframe
    season_df = pd.DataFrame(columns=['date', 'visitor', 'home', 'visitor_q1', 'home_q1', 'visitor_q2', 'home_q2',
                                      'visitor_q3', 'home_q3', 'visitor_q4', 'home_q4', 'visitor_final', 'home_final'])

    for month in months:
        season_df = season_df.append(scrape_month(season + 1, month), ignore_index=True)

    return season_df


def main():
    df = pd.DataFrame(columns=['date', 'visitor', 'home', 'visitor_q1', 'home_q1', 'visitor_q2', 'home_q2',
                               'visitor_q3', 'home_q3', 'visitor_q4', 'home_q4', 'visitor_final', 'home_final'])

    seasons = list(range(2006, 2021))
    months = ["october", "november", "december", "january", "february", "march", "april", "may", "june"]
    holdout_months = ["december", "january", "february", "march", "april", "may", "june"]
    covid_months = [["october-2019", "november", "december", "january", "february",
                    "march", "july", "august", "september", "october-2020"],
                    ["december", "january", "february", "march", "april", "may", "june", "july"]]
    for season in seasons:
        if season == 2011:
            df = df.append(scrape_season(season, holdout_months), ignore_index= True)
        elif season == 2019:
            df = df.append(scrape_season(season, covid_months[0]), ignore_index=True)
        elif season == 2020:
            df = df.append(scrape_season(season, covid_months[1]), ignore_index=True)
        else:
            df = df.append(scrape_season(season, months), ignore_index=True)

        df.to_csv('backend/data/scoring.csv')


if __name__ == '__main__':
    main()
