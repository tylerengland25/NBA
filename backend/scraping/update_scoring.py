from scraper import MonthScraper, ScoresScraper
import pandas as pd
from datetime import date


def scrape_season(season, months, latest_date, current_date):
    # Print season
    print(season)
    
    # Initialize dataframe
    season_df = pd.DataFrame()

    for month in months:
        scraper = MonthScraper(f"https://www.basketball-reference.com/leagues/NBA_{season + 1}_games-{month}.html", latest_date, current_date, ScoresScraper)
        month_df = scraper.scrape()
        season_df = pd.concat([season_df, month_df], axis=0, ignore_index=True)

    # Append season to dataframe
    season_df['season'] = season

    return season_df


def update():
    # Load data
    df = pd.read_csv('backend/data/scoring.csv')

    # Extract latest date
    dates = pd.to_datetime(df['date'])
    latest_date = dates.max()
    latest_date = date(latest_date.year, latest_date.month, latest_date.day)

    # Current date to update until
    current_date = date.today()

    # Season and months to scrape
    season = 2022
    months = ["october", "november", "december", "january", "february", "march", "april"]

    season_df = scrape_season(season, months, latest_date, current_date)
    df = pd.concat([df, season_df], axis=0, ignore_index=True)
    
    df = df.drop_duplicates(['date', 'visitor', 'home', 'team'], keep='last')
    df.to_csv('backend/data/scoring.csv', index=False)

