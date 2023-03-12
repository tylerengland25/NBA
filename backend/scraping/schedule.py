from scraper import ScheduleScraper
import pandas as pd


def scrape_season(season, months):
    # Print season
    print(season)
    
    # Initialize dataframe
    season_df = pd.DataFrame()

    # Scrape months in season
    for month in months:
        scraper = ScheduleScraper(f'https://www.basketball-reference.com/leagues/NBA_{season + 1}_games-{month}.html')
        month_df = scraper.scrape()
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