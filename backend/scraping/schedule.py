from bs4 import BeautifulSoup
from urllib.request import urlopen
import pandas as pd


def scrape_month(season, month):
    # Print month
    print("\t" + month)

    # Connect to website
    url = f"https://www.basketball-reference.com/leagues/NBA_{season}_games-{month}.html"
    html = urlopen(url)
    soup = BeautifulSoup(html, features="lxml")

    # Initialize dataframe
    month_df = pd.DataFrame()

    # Find games and iterate to find shooting data
    games = soup.find("table").find_all("tr")[1:]
    for game in games:
        row_data = game.find_all(["th", "td"])
        if len(row_data) > 1:
            # Print game info
            game_data = {'date': row_data[0].text, 'visitor': row_data[2].text, 'home': row_data[4].text}
            print(f"\t\t{game_data['date']}, {game_data['visitor']} @ {game_data['home']}")
            
            game_data = pd.DataFrame([game_data])
            month_df = pd.concat([month_df, game_data], axis=0, ignore_index=True)

    return month_df


def scrape_season(season, months):
    # Print season
    print(season)
    
    # Initialize dataframe
    season_df = pd.DataFrame()

    # Scrape months in season
    for month in months:
        month_df = scrape_month(season + 1, month)
        season_df = pd.concat([season_df, month_df], axis=0, ignore_index=True)

    # Append season to dataframe
    season_df['season'] = season

    return season_df


def update_schedule(season):
    # Months for holdout, covid and non-covid seasons
    months = ["october", "november", "december", "january", "february", "march", "april"]
    holdout_months = ["december", "january", "february", "march", "april", "may", "june"]
    covid_months = [["october-2019", "november", "december", "january", "february",
                     "march", "july", "august", "september", "october-2020"],
                    ["december", "january", "february", "march", "april", "may", "june", "july"]]

    if season == 2011:
        scrape_season(season, holdout_months).to_csv(f'backend/data/schedules/{season}.csv', index=False)
    elif season == 2019:
        scrape_season(season, covid_months[0]).to_csv(f'backend/data/schedules/{season}.csv', index=False)
    elif season == 2020:
        scrape_season(season, covid_months[1]).to_csv(f'backend/data/schedules/{season}.csv', index=False)
    elif season == 2021:
        scrape_season(season, months).to_csv(f'backend/data/schedules/{season}.csv', index=False)
    else:
        scrape_season(season, months).to_csv(f'backend/data/schedules/{season}.csv', index=False)