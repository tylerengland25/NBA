from urllib.request import urlopen
from bs4 import BeautifulSoup, Comment
import pandas as pd
from datetime import date


class Scraper:
    def __init__(self, url):
        self.url = url
        self.soup = self.get_soup()
        self.df = pd.DataFrame()

    def get_soup(self):
        html = urlopen(self.url)
        return BeautifulSoup(html, features="lxml")
    

class MonthScraper(Scraper):
    def __init__(self, url, latest_date, current_date, GameScraper):
        super().__init__(url)
        self.latest_date = latest_date
        self.current_date = current_date
        self.game_scraper = GameScraper

    def get_games(self):
        return self.soup.find("table").find_all("tr")[1:] 
    
    def get_game_data(self, game):
        row_data = game.find_all(["th", "td"])
        if len(row_data) > 1:
            return {'date': row_data[0].text, 'visitor': row_data[2].text, 'home': row_data[4].text}
        return None
    
    def convert_date(self, game_date):
        game_date = pd.to_datetime(game_date)
        return date(game_date.year, game_date.month, game_date.day)
    
    def date_between(self, game_date):
        return self.latest_date <= game_date < self.current_date

    def get_game_link(self, game):
        row_data = game.find_all(["th", "td"])
        if len(row_data) > 1:
            return row_data[6].a["href"]
        return None
    
    def merge_df(self, df):
        self.df = pd.concat([self.df, df], axis=0, ignore_index=True)
    
    def scrape(self):
        games = self.get_games()
        for game in games:
            game_data = self.get_game_data(game)
            game_date = self.convert_date(game_data['date'])
            if self.date_between(game_date) and game_data:
                print(f"\t\t{game_data['date']}, {game_data['visitor']} @ {game_data['home']}")
                link = self.get_game_link(game)
                game_df = self.game_scraper(link, game_data).scrape()
                self.merge_df(game_df)
        return self.df
    

class DetailsScraper(Scraper):
    def __init__(self, url, game_data):
        super().__init__(f"https://www.basketball-reference.com{url}")
        self.game_data = game_data
        self.team = False

    def get_basic_tables(self):
        basic_tables = []
        tables = self.soup.find_all('table')
        for table in tables:
            if " ".join(table['id'].split('-')[-2:]) == "game basic":
                basic_tables.append(table)
        return basic_tables
    
    def get_players(self, table):
        return table.find('tbody').find_all('tr')
    
    def get_player_data(self, player):
        return [data.text for data in player.find_all(['th', 'td'])]
    
    def get_player_stats(self, player_data, starter):
        if len(player_data) < 21:
            stats = {
                'date': self.game_data['date'], 'visitor': self.game_data['visitor'], 'home': self.game_data['home'],
                'team': int(self.team), 'starter': int(starter), 'player': player_data[0], 'mp': 0,
                'fg': 0, 'fga': 0, 'fg_perc': 0, '3p': 0, '3pa': 0, '3p_perc': 0,
                'ft': 0, 'fta': 0, 'ft_perc': 0, 'orb': 0, 'drb': 0, 'trb': 0,
                'ast': 0, 'stl': 0, 'blk': 0, 'tov': 0, 'pf': 0, 'pts': 0, 'plus_minus': 0
            }
        else:
            stats = {
                'date': self.game_data['date'], 'visitor': self.game_data['visitor'], 'home': self.game_data['home'],
                'team': int(self.team), 'starter': int(starter), 'player': player_data[0], 'mp': player_data[1],
                'fg': player_data[2], 'fga': player_data[3], 'fg_perc': player_data[4],
                '3p': player_data[5], '3pa': player_data[6], '3p_perc': player_data[7],
                'ft': player_data[8], 'fta': player_data[9], 'ft_perc': player_data[10],
                'orb': player_data[11], 'drb': player_data[12], 'trb': player_data[13],
                'ast': player_data[14], 'stl': player_data[15], 'blk': player_data[16],
                'tov': player_data[17], 'pf': player_data[18], 'pts': player_data[19],
                'plus_minus': player_data[20]
            }
        return stats
    
    def merge_df(self, df):
        self.df = pd.concat([self.df, df], axis=0, ignore_index=True)

    def scrape(self):
        basic_tables = self.get_basic_tables()
        for table in basic_tables:
            players = self.get_players(table)
            for index, player in enumerate(players):
                starter = True if index < 5 else False
                player_data = self.get_player_data(player)
                stats = self.get_player_stats(player_data, starter)
                self.merge_df(pd.DataFrame(stats, index=[0]))
            self.team = not self.team
        return self.df
    

class TotalsScraper(Scraper):
    def __init__(self, url, game_data):
        super().__init__(f"https://www.basketball-reference.com{url}")
        self.game_data = game_data
        self.team = False

    def get_basic_tables(self):
        basic_tables = []
        tables = self.soup.find_all('table')
        for table in tables:
            if " ".join(table['id'].split('-')[-2:]) == "game basic":
                basic_tables.append(table)
        return basic_tables
    
    def get_totals(self, table):
        totals = [td.text for td in table.find_all('tr')[-1].find_all('td')]
        team_totals = {
            'date': self.game_data['date'], 'visitor': self.game_data['visitor'], 'home': self.game_data['home'], 'team': int(self.team), 
            'fg': totals[1], 'fga': totals[2], 'fg_perc': totals[3],
            '3p': totals[4], '3pa': totals[5], '3p_perc': totals[6], 
            'ft': totals[7], 'fta': totals[8], 'ft_perc': totals[9], 
            'orb': totals[10], 'drb': totals[11], 'trb': totals[12], 
            'ast': totals[13], 'stl': totals[14], 'blk': totals[15],
            'tov': totals[16], 'pf': totals[17], 'pts': totals[18]
            }
        return team_totals
    
    def merge_df(self, df):
        self.df = pd.concat([self.df, df], axis=0, ignore_index=True)

    def scrape(self):
        basic_tables = self.get_basic_tables()
        for table in basic_tables:
            team_totals = self.get_totals(table)
            self.merge_df(pd.DataFrame(team_totals, index=[0]))
            self.team = not self.team
        return self.df
    

class ScoresScraper(Scraper):
    def __init__(self, url, game_data):
        super().__init__(f"https://www.basketball-reference.com{url}")
        self.game_data = game_data

    def get_table(self):
        div = self.soup.find('div', attrs={'id': 'all_line_score'})
        for element in div(text=lambda text: isinstance(text, Comment)):
            if BeautifulSoup(element, features="lxml").find('table', attrs={'id': 'line_score'}):
                return BeautifulSoup(element, features="lxml").find('table', attrs={'id': 'line_score'})
    
    def get_scores(self, table):
        scores = [int(score.text) for score in table.find_all('td')]
        if len(scores) == 10:
            home_row = {
                'date': self.game_data['date'], 'visitor': self.game_data['visitor'], 'home': self.game_data['home'],
                'team': 1, 'q1': scores[5], 'q2': scores[6], 'q3': scores[7], 'q4': scores[8],
                'final': scores[9]
            }
            visitor_row = {
                'date': self.game_data['date'], 'visitor': self.game_data['visitor'], 'home': self.game_data['home'],
                'team': 0, 'q1': scores[0], 'q2': scores[1], 'q3': scores[2], 'q4': scores[3],
                'final': scores[4]
            }
        elif len(scores) == 12:
            home_row = {
                'date': self.game_data['date'], 'visitor': self.game_data['visitor'], 'home': self.game_data['home'],
                'team': 1, 'q1': scores[6], 'q2': scores[7], 'q3': scores[8], 'q4': scores[9],
                'ot1': scores[10],
                'final': scores[11]
            }
            visitor_row = {
                'date': self.game_data['date'], 'visitor': self.game_data['visitor'], 'home': self.game_data['home'],
                'team': 0, 'q1': scores[0], 'q2': scores[1], 'q3': scores[2], 'q4': scores[3],
                'ot1': scores[4],
                'final': scores[5]
            }
        elif len(scores) == 14:
            home_row = {
                'date': self.game_data['date'], 'visitor': self.game_data['visitor'], 'home': self.game_data['home'],
                'team': 1, 'q1': scores[7], 'q2': scores[8], 'q3': scores[9], 'q4': scores[10],
                'ot1': scores[11], 'ot2': scores[12],
                'final': scores[13]
            }
            visitor_row = {
                'date': self.game_data['date'], 'visitor': self.game_data['visitor'], 'home': self.game_data['home'],
                'team': 0, 'q1': scores[0], 'q2': scores[1], 'q3': scores[2], 'q4': scores[3],
                'ot1': scores[4], 'ot2': scores[5],
                'final': scores[6]
            }
        elif len(scores) == 16:
            home_row = {
                'date': self.game_data['date'], 'visitor': self.game_data['visitor'], 'home': self.game_data['home'],
                'team': 1, 'q1': scores[8], 'q2': scores[9], 'q3': scores[10], 'q4': scores[11],
                'ot1': scores[12], 'ot2': scores[13], 'ot3': scores[14],
                'final': scores[15]
            }
            visitor_row = {
                'date': self.game_data['date'], 'visitor': self.game_data['visitor'], 'home': self.game_data['home'],
                'team': 0, 'q1': scores[0], 'q2': scores[1], 'q3': scores[2], 'q4': scores[3],
                'ot1': scores[4], 'ot2': scores[5], 'ot3': scores[6],
                'final': scores[7]
            }
        else:
            home_row = {
                'date': self.game_data['date'], 'visitor': self.game_data['visitor'], 'home': self.game_data['home'],
                'team': 1, 'q1': scores[9], 'q2': scores[10], 'q3': scores[11], 'q4': scores[12],
                'ot1': scores[13], 'ot2': scores[14], 'ot3': scores[15], 'ot4': scores[16],
                'final': scores[17]
            }
            visitor_row = {
                'date': self.game_data['date'], 'visitor': self.game_data['visitor'], 'home': self.game_data['home'],
                'team': 0, 'q1': scores[0], 'q2': scores[1], 'q3': scores[2], 'q4': scores[3],
                'ot1': scores[4], 'ot2': scores[5], 'ot3': scores[6], 'ot4': scores[7],
                'final': scores[8]
            }

        return home_row, visitor_row
    
    def merge_df(self, df):
        self.df = pd.concat([self.df, df], axis=0, ignore_index=True)

    def scrape(self):
        table = self.get_table()
        home_row, visitor_row = self.get_scores(table)
        self.merge_df(pd.DataFrame(home_row, index=[0]))
        self.merge_df(pd.DataFrame(visitor_row, index=[0]))
        return self.df
    

class ShootingScraper(Scraper):
    def __init__(self, url, game_data):
        link = url.split('/')
        link.insert(2, 'shot-chart')
        link = '/'.join(link)
        super().__init__(f"https://www.basketball-reference.com{link}")
        self.game_data = game_data
        self.team = False

    def get_tables(self):
        return self.soup.find_all('table')
    
    def get_shooting_data(self, data):
        quarter_dict = {
            '1st': 'q1', '2nd': 'q2', '3rd': 'q3', '4th': 'q4', 
            'OT': 'ot1', '2OT': 'ot2', '3OT': 'ot3', '4OT': 'ot4'
        }
        shooting_data = {
            'date': self.game_data['date'], 'visitor': self.game_data['visitor'], 'home': self.game_data['home'], 
            'team': self.team, 'quarter': quarter_dict[data[0]], 
            'fg': data[1], 'fga': data[2], 'fg_perc': data[3], 
            '2p': data[4], '2pa': data[5], '2p_perc': data[6], 
            '3p': data[7], '3pa': data[8], '3p_perc': data[9], 
            'efg_perc': data[10], 'ast': data[11], 'ast_perc': data[12]
        }
        return shooting_data
    
    def merge_df(self, df):
        self.df = pd.concat([self.df, df], axis=0, ignore_index=True)
    
    def scrape(self):
        tables = self.get_tables()
        for table in tables:
            quarters = table.find_all('tr')[1:-1]
            for quarter in quarters:
                data = [x.text for x in quarter.find_all(['td', 'th'])]
                shooting_data = self.get_shooting_data(data)
                self.merge_df(pd.DataFrame(shooting_data, index=[0]))
            self.team = not self.team
        return self.df