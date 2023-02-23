import requests
import pandas as pd


# An api key is emailed to you when you sign up to a plan
# Get a free API key at https://api.the-odds-api.com/
API_KEY = 'bad33b9645e692dfc2f262f050de57d9'

SPORT = 'basketball_nba' # use the sport_key from the /sports endpoint below, or use 'upcoming' to see the next 8 games across all sports

REGIONS = 'us' # uk | us | eu | au. Multiple can be specified if comma delimited

MARKETS = 'h2h' # h2h | spreads | totals. Multiple can be specified if comma delimited

PROP_MARKETS = 'player_rebounds'

ODDS_FORMAT = 'american' # decimal | american

DATE_FORMAT = 'iso' # iso | unix

PATH_TO_FILE = '/home/tylerengland/NBA/backend/data/odds/player_props/rebounds.csv'


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
#
# Now get a list of live & upcoming games for the sport you want, along with odds for different bookmakers
# This will deduct from the usage quota
# The usage quota cost = [number of markets specified] x [number of regions specified]
# For examples of usage quota costs, see https://the-odds-api.com/liveapi/guides/v4/#usage-quota-costs
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

odds_response = requests.get(f'https://api.the-odds-api.com/v4/sports/{SPORT}/odds', params={
    'api_key': API_KEY,
    'regions': REGIONS,
    'markets': MARKETS,
    'oddsFormat': ODDS_FORMAT,
    'dateFormat': DATE_FORMAT,
})

if odds_response.status_code != 200:
    print(f'Failed to get odds: status_code {odds_response.status_code}, response body {odds_response.text}')

else:
    odds_json = odds_response.json()
    print('Number of events:', len(odds_json))
    print('Remaining requests', odds_response.headers['x-requests-remaining'])
    print('Used requests', odds_response.headers['x-requests-used'])

    # Get each event
    rows = []
    for event in odds_json:
        EVENT_ID = event['id']
        events_response = requests.get(f'https://api.the-odds-api.com/v4/sports/{SPORT}/events/{EVENT_ID}/odds', params={
            'api_key': API_KEY,
            'regions': REGIONS,
            'markets': PROP_MARKETS,
            'oddsFormat': ODDS_FORMAT,
            'dateFormat': DATE_FORMAT,
        })
        events_json = events_response.json()
        game_info = {
            'date': events_json['commence_time'],
            'home': events_json['home_team'],
            'away': events_json['away_team']
        }
        for book in events_json['bookmakers']:
            book_info = {
                'book': book['title'],
                'last_update': book['markets'][0]['last_update']
            }
            for line in book['markets'][0]['outcomes']:
                line_info = {
                    'type': line['name'],
                    'player': line['description'],
                    'price': line['price'],
                    'line': line['point']
                }
                row = {
                    'date': game_info['date'], 'home': game_info['home'], 'away': game_info['away'],
                    'player': line_info['player'], 'type': line_info['type'], 'line': line_info['line'], 'price': line_info['price'],
                    'book': book_info['book'], 'last_updated': book_info['last_update']
                }
                rows.append(row)
    lines_df = pd.DataFrame(rows)
    lines_df.to_csv(PATH_TO_FILE, index=False)
            