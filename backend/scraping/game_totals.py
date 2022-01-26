from bs4 import BeautifulSoup
from urllib.request import urlopen
import pandas as pd


def scrape_game(link, meta_data):
    # Connect to website
    url = "https://www.basketball-reference.com{}".format(link)
    html = urlopen(url)
    soup = BeautifulSoup(html, features="lxml")

    # Totals dictionary
    game_df = pd.DataFrame(
        columns=['date', 'visitor', 'home', 'team', 'fg', 'fga', 'fg_perc', '3p', '3pa', '3p_perc',
                 'ft', 'fta', 'ft_perc', 'orb', 'drb', 'trb', 'ast', 'stl', 'blk', 'tov', 'pf', 'pts'])

    # Home: 1, Visitor: 0
    team = 0

    # Find gamed details table and return total stats for each team
    tables = soup.find_all('table')
    tables = [tables[0], tables[8]]
    for table in tables:
        totals_tag = table.find_all('tr')[-1].find_all('td')[1:-1]
        totals = [td.text for td in totals_tag]
        team_totals = {'date': meta_data['date'], 'visitor': meta_data['visitor'], 'home': meta_data['home'],
                       'team': team, 'fg': totals[0], 'fga': totals[1], 'fg_perc': totals[2], '3p': totals[3],
                       '3pa': totals[4], '3p_perc': totals[5], 'ft': totals[6], 'fta': totals[7], 'ft_perc': totals[8],
                       'orb': totals[9], 'drb': totals[10], 'trb': totals[11], 'ast': totals[12], 'stl': totals[13],
                       'blk': totals[14], 'tov': totals[15], 'pf': totals[16], 'pts': totals[17]}
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
                columns=['date', 'visitor', 'home', 'team', 'fg', 'fga', 'fg_perc','3p', '3pa', '3p_perc',
                         'ft', 'fta', 'ft_perc', 'orb', 'drb', 'trb', 'ast', 'stl', 'blk', 'tov', 'pf', 'pts'])

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
                columns=['date', 'visitor', 'home', 'team', 'fg', 'fga', 'fg_perc','3p', '3pa', '3p_perc',
                         'ft', 'fta', 'ft_perc', 'orb', 'drb', 'trb', 'ast', 'stl', 'blk', 'tov', 'pf', 'pts'])

    for month in months:
        season_df = season_df.append(scrape_month(season + 1, month), ignore_index=True)

    return season_df


def main():
    df = pd.DataFrame(
                columns=['date', 'visitor', 'home', 'team', 'fg', 'fga', 'fg_perc','3p', '3pa', '3p_perc',
                         'ft', 'fta', 'ft_perc', 'orb', 'drb', 'trb', 'ast', 'stl', 'blk', 'tov', 'pf', 'pts'])

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

        df.to_csv('backend/data/game_details_total.csv')


if __name__ == '__main__':
    main()
