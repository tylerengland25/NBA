from bs4 import BeautifulSoup
from urllib.request import urlopen
import pandas as pd


def scrape_game(link, meta_data):
    # Connect to website
    url = "https://www.basketball-reference.com{}".format(link)
    html = urlopen(url)
    soup = BeautifulSoup(html, features="lxml")

    # Advanced totals dictionary
    game_df = pd.DataFrame(
        columns=['date', 'visitor', 'home', 'team', 'ts_perc', 'efg_perc', '3par', 'ftr', 'orb_perc', 'drb_perc',
                 'trb_perc', 'ast_perc', 'stl_perc', 'blk_perc', 'tov_perc', 'usg_perc', 'ortg', 'drtg'])

    # Home: 1, Visitor: 0
    team = 0

    # Find advanced gamed details table and return total stats for each team
    tables = soup.find_all('table')
    tables = [tables[7], tables[15]]
    for table in tables:
        totals_tag = table.find_all('tr')[-1].find_all('td')[1:-1]
        totals = [td.text for td in totals_tag]
        team_totals = {'date': meta_data['date'], 'visitor': meta_data['visitor'], 'home': meta_data['home'],
                       'team': team, 'ts_perc': totals[0], 'efg_perc': totals[1], '3par': totals[2], 'ftr': totals[3],
                       'orb_perc': totals[4], 'drb_perc': totals[5], 'trb_perc': totals[6], 'ast_perc': totals[7],
                       'stl_perc': totals[8], 'blk_perc': totals[9], 'tov_perc': totals[10], 'usg_perc': totals[11],
                       'ortg': totals[12], 'drtg': totals[13]}
        game_df = game_df.append(team_totals, ignore_index=True)

        team = 1

    return game_df


def scrape_month(season, month):
    print("\t" + month)
    # Connect to website
    url = "https://www.basketball-reference.com/leagues/NBA_{}_games-{}.html".format(str(season), month)
    html = urlopen(url)
    soup = BeautifulSoup(html, features="lxml")

    # Month dataframe
    month_df = pd.DataFrame(
        columns=['date', 'visitor', 'home', 'team', 'ts_perc', 'efg_perc', '3par', 'ftr', 'orb_perc', 'drb_perc',
                 'trb_perc', 'ast_perc', 'stl_perc', 'blk_perc', 'tov_perc', 'usg_perc', 'ortg', 'drtg'])

    # Find games and iterate to find scoring data
    games = soup.find("table").find_all("tr")[1:]
    for game in games:
        row_data = game.find_all(["th", "td"])
        if len(row_data) > 1:
            print("\t\t" + str(row_data[0].text) + ", " + row_data[2].text + " @ " + row_data[4].text)
            game_data = {'date': row_data[0].text, 'visitor': row_data[2].text, 'home': row_data[4].text}
            link = row_data[6].a["href"]
            month_df = month_df.append(scrape_game(link, game_data), ignore_index=True)

    return month_df


def scrape_season(season, months):
    print(season)
    # Season dataframe
    season_df = pd.DataFrame(
        columns=['date', 'visitor', 'home', 'team', 'ts_perc', 'efg_perc', '3par', 'ftr', 'orb_perc', 'drb_perc',
                 'trb_perc', 'ast_perc', 'stl_perc', 'blk_perc', 'tov_perc', 'usg_perc', 'ortg', 'drtg'])

    for month in months:
        season_df = season_df.append(scrape_month(season + 1, month), ignore_index=True)

    return season_df


def main():
    df = pd.DataFrame(
        columns=['date', 'visitor', 'home', 'team', 'ts_perc', 'efg_perc', '3par', 'ftr', 'orb_perc', 'drb_perc',
                 'trb_perc', 'ast_perc', 'stl_perc', 'blk_perc', 'tov_perc', 'usg_perc', 'ortg', 'drtg'])

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

        df.to_csv('backend/data/advanced_game_details_total.csv')


if __name__ == '__main__':
    main()
