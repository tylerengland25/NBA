from bs4 import BeautifulSoup
from urllib.request import urlopen
import pandas as pd


def scrape_month(season, month):
    print("\t" + month)
    # Connect to website
    url = "https://www.basketball-reference.com/leagues/NBA_{}_games-{}.html".format(str(season), month)
    html = urlopen(url)
    soup = BeautifulSoup(html, features="lxml")

    # Month datframe
    cols = ['date', 'visitor', 'home', 'time']
    month_df = pd.DataFrame(columns=cols)

    # Find games and iterate to find shooting data
    games = soup.find("table").find_all("tr")[1:]
    for game in games:
        row_data = game.find_all(["th", "td"])
        if len(row_data) > 1:
            print("\t\t" + str(row_data[0].text) + ", " + row_data[2].text + " @ " + row_data[4].text)
            game_data = {
                'date': row_data[0].text, 'time': row_data[1].text,
                'visitor': row_data[2].text, 'home': row_data[4].text
            }
            month_df = month_df.append(game_data, ignore_index=True)

    return month_df


def scrape_season(season, months):
    print(season)
    # Season dataframe
    cols = ['date', 'visitor', 'home', 'time']
    season_df = pd.DataFrame(columns=cols)

    # Scrape months in season
    for month in months:
        season_df = season_df.append(scrape_month(season + 1, month), ignore_index=True)

    return season_df


def main():
    # Scrape seasons
    seasons = list(range(2006, 2022))
    months = ["october", "november", "december", "january", "february", "march", "april", "may", "june"]
    holdout_months = ["december", "january", "february", "march", "april", "may", "june"]
    covid_months = [["october-2019", "november", "december", "january", "february",
                     "march", "july", "august", "september", "october-2020"],
                    ["december", "january", "february", "march", "april", "may", "june", "july"]]
    for season in seasons:
        if season == 2011:
            scrape_season(season, holdout_months).to_csv(f'backend/data/schedules/{season}.csv')
        elif season == 2019:
            scrape_season(season, covid_months[0]).to_csv(f'backend/data/schedules/{season}.csv')
        elif season == 2020:
            scrape_season(season, covid_months[1]).to_csv(f'backend/data/schedules/{season}.csv')
        elif season == 2021:
            scrape_season(season, months[:-2]).to_csv(f'backend/data/schedules/{season}.csv')
        else:
            scrape_season(season, months).to_csv(f'backend/data/schedules/{season}.csv')


if __name__ == '__main__':
    main()
