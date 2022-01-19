from bs4 import BeautifulSoup
from urllib.request import urlopen
import pandas as pd


def scrape_game(link):
    # Connect to website
    link = link.split('/')
    link.insert(2, 'shot-chart')
    url = "https://www.basketball-reference.com{}".format('/'.join(link))
    html = urlopen(url)
    soup = BeautifulSoup(html, features="lxml")

    # Find shooting table and return quarter shooting stats for both teams
    shooting_data = {}
    tables = soup.find_all('table')
    home_visitor = 0
    for table in tables:
        home_visitor += 1
        rows = table.find_all('tr')
        for row in rows[1:]:
            data = row.find_all(['th', 'td'])
            data = [td.text for td in data]

            # Which team
            team = 'visitor' if home_visitor == 1 else 'home'

            # Which quarter
            if data[0] == '1st':
                quarter = 'q1'
            elif data[0] == '2nd':
                quarter = 'q2'
            elif data[0] == '3rd':
                quarter = 'q3'
            elif data[0] == '4th':
                quarter = 'q4'
            else:
                quarter = 'total'

            shooting_data.update(
                {'fg_{}_{}'.format(team, quarter): data[1], 'fga_{}_{}'.format(team, quarter): data[2],
                 'fg_perc_{}_{}'.format(team, quarter): data[3], '2p_{}_{}'.format(team, quarter): data[4],
                 '2pa_{}_{}'.format(team, quarter): data[5], '2p_perc_{}_{}'.format(team, quarter): data[6],
                 '3p_{}_{}'.format(team, quarter): data[7], '3pa_{}_{}'.format(team, quarter): data[8],
                 '3p_perc_{}_{}'.format(team, quarter): data[9], 'efg_perc_{}_{}'.format(team, quarter): data[10],
                 'ast_{}_{}'.format(team, quarter): data[11], 'ast_perc_{}_{}'.format(team, quarter): data[12]
                 }
            )

    return shooting_data


def scrape_month(season, month):
    print("\t" + month)
    # Connect to website
    url = "https://www.basketball-reference.com/leagues/NBA_{}_games-{}.html".format(str(season), month)
    html = urlopen(url)
    soup = BeautifulSoup(html, features="lxml")

    # Month datframe
    stats = ['fg', 'fga', 'fg_perc', '2p', '2pa', '2p_perc', '3p', '3pa', '3p_perc', 'efg_perc', 'ast', 'ast_perc']
    quarters = ['q1', 'q2', 'q3', 'q4', 'total']
    teams = ['visitor', 'home']
    quarter_stats = [stat + '_' + team + '_' + quarter for quarter in quarters for stat in stats for team in teams]
    cols = ['date', 'visitor', 'home'] + quarter_stats
    month_df = pd.DataFrame(columns=cols)

    # Find games and iterate to find shooting data
    games = soup.find("table").find_all("tr")[1:]
    for game in games:
        row_data = game.find_all(["th", "td"])
        if len(row_data) > 1:
            print("\t\t" + str(row_data[0].text) + ", " + row_data[2].text + " @ " + row_data[4].text)
            game_data = {'date': row_data[0].text, 'visitor': row_data[2].text, 'home': row_data[4].text}
            link = row_data[6].a["href"]
            game_data.update(scrape_game(link))
            month_df = month_df.append(game_data, ignore_index=True)

    return month_df


def scrape_season(season, months):
    print(season)
    # Season dataframe
    stats = ['fg', 'fga', 'fg_perc', '2p', '2pa', '2p_perc', '3p', '3pa', '3p_perc', 'efg_perc', 'ast', 'ast_perc']
    quarters = ['q1', 'q2', 'q3', 'q4', 'total']
    teams = ['visitor', 'home']
    quarter_stats = [stat + '_' + team + '_' + quarter for quarter in quarters for stat in stats for team in teams]
    cols = ['date', 'visitor', 'home'] + quarter_stats
    season_df = pd.DataFrame(columns=cols)

    # Scrape months in season
    for month in months:
        season_df = season_df.append(scrape_month(season + 1, month), ignore_index=True)

    return season_df


def main():
    # Create main shooting dataframe
    stats = ['fg', 'fga', 'fg_perc', '2p', '2pa', '2p_perc', '3p', '3pa', '3p_perc', 'efg_perc', 'ast', 'ast_perc']
    quarters = ['q1', 'q2', 'q3', 'q4', 'total']
    teams = ['visitor', 'home']
    quarter_stats = [stat + '_' + team + '_' + quarter for quarter in quarters for stat in stats for team in teams]
    cols = ['date', 'visitor', 'home'] + quarter_stats
    df = pd.DataFrame(columns=cols)

    # Scrape seasons
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

        df.to_csv('backend/data/shooting.csv')


if __name__ == '__main__':
    main()
