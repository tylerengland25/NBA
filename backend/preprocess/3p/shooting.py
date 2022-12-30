import datetime
import numpy as np
import pandas as pd


def load_data():
    df = pd.read_csv('backend/data/shooting.csv').drop(['Unnamed: 0'], axis=1)

    # Convert 'date' column to Date object
    df['date'] = pd.to_datetime(df['date'])

    # Conver 'team' column to Team Name
    df['team'] = np.where(df['team'], df['home'], df['visitor'])

    # Merge in opponents (see team defensive stats)
    df = pd.merge(
        df,
        df,
        left_on=['date', 'visitor', 'home', 'quarter'],
        right_on=['date', 'visitor', 'home', 'quarter'],
        suffixes=('', '_opp'),
        how='left')

    df = df[df['team'] != df['team_opp']]
    total_df = df[df['quarter'] == 'total']

    return total_df


def load_next_slate(total_df):
    df = pd.read_csv('backend/data/schedules/2022.csv')
    df['date'] = pd.to_datetime(df['date'])

    next_date = set(df['date'].unique()).difference(set(total_df['date'].unique()))
    next_date = pd.Series(list(next_date)).min()

    games = df[df['date'] == next_date]

    for index, game in games.iterrows():
        total_df = total_df.append(
            {'date': game.date, 'visitor': game.visitor, 'home': game.home, 'team': game.home},
            ignore_index=True
        )
        total_df = total_df.append(
            {'date': game.date, 'visitor': game.visitor, 'home': game.home, 'team': game.visitor},
            ignore_index=True
        )

    next_slate = total_df[total_df['date'] == next_date].copy()

    return next_slate


def last_15_date(team, df):
    schedule = df[df['team'] == team].sort_values(by='date', ascending=False).reset_index().drop(['index'], axis=1)
    date_1, date_2 = schedule.iloc[0]['date'], schedule.iloc[1]['date']
    date_3, date_4 = schedule.iloc[2]['date'], schedule.iloc[3]['date']
    date_5, date_6 = schedule.iloc[4]['date'], schedule.iloc[5]['date']
    date_7, date_8 = schedule.iloc[6]['date'], schedule.iloc[7]['date']
    date_9, date_10 = schedule.iloc[8]['date'], schedule.iloc[9]['date']
    date_11, date_12 = schedule.iloc[10]['date'], schedule.iloc[11]['date']
    date_13, date_14 = schedule.iloc[12]['date'], schedule.iloc[13]['date']
    date_15 = schedule.iloc[14]['date']
    return [date_1, date_2, date_3, date_4, date_5, date_6, date_7, date_8,
            date_9, date_10, date_11, date_12, date_13, date_14, date_15]


def next_slate_last_15(next_slate, total_df):
    next_slate['dates'] = next_slate.apply(lambda x: last_15_date(x.team, total_df), axis=1)
    next_slate['date_1'] = next_slate['dates'].apply(lambda x: x[0])
    next_slate['date_2'] = next_slate['dates'].apply(lambda x: x[1])
    next_slate['date_3'] = next_slate['dates'].apply(lambda x: x[2])
    next_slate['date_4'] = next_slate['dates'].apply(lambda x: x[3])
    next_slate['date_5'] = next_slate['dates'].apply(lambda x: x[4])
    next_slate['date_6'] = next_slate['dates'].apply(lambda x: x[5])
    next_slate['date_7'] = next_slate['dates'].apply(lambda x: x[6])
    next_slate['date_8'] = next_slate['dates'].apply(lambda x: x[7])
    next_slate['date_9'] = next_slate['dates'].apply(lambda x: x[8])
    next_slate['date_10'] = next_slate['dates'].apply(lambda x: x[9])
    next_slate['date_11'] = next_slate['dates'].apply(lambda x: x[10])
    next_slate['date_12'] = next_slate['dates'].apply(lambda x: x[11])
    next_slate['date_13'] = next_slate['dates'].apply(lambda x: x[12])
    next_slate['date_14'] = next_slate['dates'].apply(lambda x: x[13])
    next_slate['date_15'] = next_slate['dates'].apply(lambda x: x[14])

    return next_slate


def merge_last_15(next_slate, total_df):
    # Define statistics
    stats = ['fg', 'fga', '2p', '2pa', '3p', '3pa', 'ast',
             'fg_opp', 'fga_opp', '2p_opp', '2pa_opp', '3p_opp', '3pa_opp', 'ast_opp']

    # X column names to merge on
    x_cols = ['date', 'team'] + stats

    # Dataframe of target (3pt made by each team) and of variables (last 5 games stats for each team)
    dates = ['_1', '_2', '_3', '_4', '_5', '_6', '_7', '_8', '_9', '_10', '_11', '_12', '_13', '_14', '_15']
    for date in dates:
        next_slate = pd.merge(
            next_slate,
            total_df[x_cols],
            left_on=['date' + date, 'team'],
            right_on=['date', 'team'],
            how='left',
            suffixes=('', date)
        )

    return next_slate


def preprocess(next_slate):
    # Define statistics
    stats = ['fg', 'fga', '2p', '2pa', '3p', '3pa', 'ast',
             'fg_opp', 'fga_opp', '2p_opp', '2pa_opp', '3p_opp', '3pa_opp', 'ast_opp']

    perc_stats = ['fg_perc', '2p_perc', '3p_perc', 'efg_perc', 'ast_perc',
                  'fg_perc_opp', '2p_perc_opp', '3p_perc_opp', 'efg_perc_opp', 'ast_perc_opp']

    dates = ['_1', '_2', '_3', '_4', '_5', '_6', '_7', '_8', '_9', '_10', '_11', '_12', '_13', '_14', '_15']

    # Calculate mean for each stat over a team's last performance
    for stat in stats:
        next_slate[stat + '_last_15'] = 0
        next_slate[stat + '_last_3'] = 0
        next_slate[stat + '_last_1'] = 0

        for date in dates:
            # Last 15 games
            next_slate[stat + '_last_15'] = next_slate[stat + '_last_15'] + next_slate[stat + date]

            # Last 3 games
            if date in ['_1', '_2', '_3']:
                next_slate[stat + '_last_3'] = next_slate[stat + '_last_3'] + next_slate[stat + date]

            # Last game
            if date in ['_1']:
                next_slate[stat + '_last_1'] = next_slate[stat + '_last_1'] + next_slate[stat + date]

        next_slate[stat + '_last_15'] = next_slate[stat + '_last_15'] / 15
        next_slate[stat + '_last_3'] = next_slate[stat + '_last_3'] / 3

    # Calculate difference between last 15 games, 3 games and last game
    for stat in stats:
        next_slate[stat + '_trend_3'] = next_slate[stat + '_last_15'] - next_slate[stat + '_last_3']
        next_slate[stat + '_trend_1'] = next_slate[stat + '_last_15'] - next_slate[stat + '_last_1']

    # Sum stats for opposing teams for each game
    next_slate = next_slate.groupby(['date', 'visitor', 'home']).sum()

    # Percentages for matchup
    for perc in perc_stats:
        stat = perc.split('_')[0]
        opp = perc.split('_')[-1]
        if opp == 'opp':
            if stat == 'ast':
                next_slate[perc + '_last_15'] = next_slate[stat + '_opp_last_15'] / next_slate['fg_opp_last_15']
                next_slate[perc + '_last_3'] = next_slate[stat + '_opp_last_3'] / next_slate['fg_opp_last_3']
                next_slate[perc + '_last_1'] = next_slate[stat + '_opp_last_1'] / next_slate['fg_opp_last_1']
            elif stat == 'efg':
                next_slate[perc + '_last_15'] = \
                    (next_slate['fg_opp_last_15'] + (.5 * next_slate['3p_opp_last_15'])) / next_slate['fga_opp_last_15']
                next_slate[perc + '_last_3'] = \
                    (next_slate['fg_opp_last_3'] + (.5 * next_slate['3p_opp_last_3'])) / next_slate['fga_opp_last_3']
                next_slate[perc + '_last_1'] = \
                    (next_slate['fg_opp_last_1'] + (.5 * next_slate['3p_opp_last_1'])) / next_slate['fga_opp_last_1']
            else:
                next_slate[perc + '_last_15'] = next_slate[stat + '_opp_last_15'] / next_slate[stat + 'a_opp_last_15']
                next_slate[perc + '_last_3'] = next_slate[stat + '_opp_last_3'] / next_slate[stat + 'a_opp_last_3']
                next_slate[perc + '_last_1'] = next_slate[stat + '_opp_last_1'] / next_slate[stat + 'a_opp_last_1']
        else:
            if stat == 'ast':
                next_slate[perc + '_last_15'] = next_slate[stat + '_last_15'] / next_slate['fg_last_15']
                next_slate[perc + '_last_3'] = next_slate[stat + '_last_3'] / next_slate['fg_last_3']
                next_slate[perc + '_last_1'] = next_slate[stat + '_last_1'] / next_slate['fg_last_1']
            elif stat == 'efg':
                next_slate[perc + '_last_15'] = \
                    (next_slate['fg_last_15'] + (.5 * next_slate['3p_last_15'])) / next_slate['fga_last_15']
                next_slate[perc + '_last_3'] = \
                    (next_slate['fg_last_3'] + (.5 * next_slate['3p_last_3'])) / next_slate['fga_last_3']
                next_slate[perc + '_last_1'] = \
                    (next_slate['fg_last_1'] + (.5 * next_slate['3p_last_1'])) / next_slate['fga_last_1']
            else:
                next_slate[perc + '_last_15'] = next_slate[stat + '_last_15'] / next_slate[stat + 'a_last_15']
                next_slate[perc + '_last_3'] = next_slate[stat + '_last_3'] / next_slate[stat + 'a_last_3']
                next_slate[perc + '_last_1'] = next_slate[stat + '_last_1'] / next_slate[stat + 'a_last_1']

    # Keep columns
    stats_15 = [stat + '_last_15' for stat in stats]
    stats_3 = [stat + '_last_3' for stat in stats]
    stats_1 = [stat + '_last_1' for stat in stats]
    trend_3 = [stat + '_trend_3' for stat in stats]
    trend_1 = [stat + '_trend_1' for stat in stats]
    last_15 = next_slate[stats_1 + stats_3 + stats_15 + perc_stats + trend_1 + trend_3]

    last_15 = last_15.dropna(axis=0)

    return last_15


def input_data(next_slate):
    cols = ['3pa_last_15', '3p_last_15', '3pa_last_3', '3pa_last_1', '3pa_opp_last_15', '3p_last_3', '3p_opp_last_15',
            '3pa_opp_last_3', '3p_opp_last_3', '3p_last_1', '3pa_opp_last_1']

    next_slate = next_slate[cols]
    next_slate = next_slate.reset_index()
    next_slate['date'] = next_slate['date'].apply(lambda x: datetime.date(x.year, x.month, x.day))

    return next_slate


def merge_input_data(next_slate):
    inputs = pd.read_csv('backend/data/inputs/3p/shooting.csv').drop(['Unnamed: 0'], axis=1)

    inputs = pd.concat(
        [inputs, next_slate]
    )
    inputs['date'] = pd.to_datetime(inputs['date'])
    inputs['date'] = inputs['date'].apply(lambda x: datetime.date(x.year, x.month, x.day))

    inputs = inputs.drop_duplicates(['date', 'visitor', 'home'], keep='last').reset_index().drop(['index'], axis=1)

    inputs.to_csv('backend/data/inputs/3p/shooting.csv')


def main():
    # Load totals
    total_df = load_data()

    # Load schedule for next games (not scraped games)
    next_slate = load_next_slate(total_df)

    # Last 15 dates of next slate
    next_slate = next_slate_last_15(next_slate, total_df)

    # Merge last 15 games of data
    next_slate = merge_last_15(next_slate, total_df)

    # Compute averages
    next_slate = preprocess(next_slate)

    # Input dataframe
    next_slate = input_data(next_slate)

    # Merge next_slate into input data
    merge_input_data(next_slate)


if __name__ == '__main__':
    main()
