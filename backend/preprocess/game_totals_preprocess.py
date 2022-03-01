import pandas as pd
import numpy as np
from itertools import product
from scipy.stats import pearsonr


def last_15_date(team, date, df):
    schedule = df[df['team'] == team].sort_values(by='date').reset_index()
    date_index = schedule[schedule['date'] == date].index[0]
    if date_index - 15 < 0:
        return None, None, None, None, None, None, None, None, None, None, None, None, None, None, None
    else:
        date_1, date_2 = schedule.iloc[date_index - 1]['date'], schedule.iloc[date_index - 2]['date']
        date_3, date_4 = schedule.iloc[date_index - 3]['date'], schedule.iloc[date_index - 4]['date']
        date_5, date_6 = schedule.iloc[date_index - 5]['date'], schedule.iloc[date_index - 6]['date']
        date_7, date_8 = schedule.iloc[date_index - 7]['date'], schedule.iloc[date_index - 8]['date']
        date_9, date_10 = schedule.iloc[date_index - 9]['date'], schedule.iloc[date_index - 10]['date']
        date_11, date_12 = schedule.iloc[date_index - 11]['date'], schedule.iloc[date_index - 12]['date']
        date_13, date_14 = schedule.iloc[date_index - 13]['date'], schedule.iloc[date_index - 14]['date']
        date_15 = schedule.iloc[date_index - 15]['date']
        return date_1, date_2, date_3, date_4, date_5, date_6, date_7, date_8, date_9, date_10, date_11, date_12, date_13, date_14, date_15


def z_score(value, mean, std):
    return (value - mean) / std


def perc_diff(value, mean):
    return (value - mean) / mean


def preprocess():
    # Load data
    df = pd.read_csv('backend/data/totals/game_totals.csv').drop(['Unnamed: 0'], axis=1)

    # Convert 'date' column to Date object
    df['date'] = pd.to_datetime(df['date'])

    # Conver 'team' column to Team Name
    df['team'] = np.where(df['team'], df['home'], df['visitor'])

    # Statistics
    stats = ['fg', 'fga', 'fg_perc', '3p', '3pa', '3p_perc', 'ft', 'fta', 'ft_perc',
             'orb', 'drb', 'trb', 'ast', 'stl', 'blk', 'tov', 'pf', 'pts']

    # Return ten lastest dates team played
    df['dates'] = df.apply(lambda x: last_15_date(x.team, x.date, df), axis=1)
    df['date_1'], df['date_2'] = df['dates'].apply(lambda x: x[0]), df['dates'].apply(lambda x: x[1])
    df['date_3'], df['date_4'] = df['dates'].apply(lambda x: x[2]), df['dates'].apply(lambda x: x[3])
    df['date_5'], df['date_6'] = df['dates'].apply(lambda x: x[4]), df['dates'].apply(lambda x: x[5])
    df['date_7'], df['date_8'] = df['dates'].apply(lambda x: x[6]), df['dates'].apply(lambda x: x[7])
    df['date_9'], df['date_10'] = df['dates'].apply(lambda x: x[8]), df['dates'].apply(lambda x: x[9])
    df['date_11'], df['date_12'] = df['dates'].apply(lambda x: x[10]), df['dates'].apply(lambda x: x[11])
    df['date_13'], df['date_14'] = df['dates'].apply(lambda x: x[12]), df['dates'].apply(lambda x: x[13])
    df['date_15'] = df['dates'].apply(lambda x: x[14])

    # X and y column names to merge on
    y_cols = df.columns
    x_cols = ['date', 'team'] + stats

    last_15_games = df[y_cols]
    last_15_games['target'] = last_15_games['3p']
    X = df[x_cols]

    # Dataframe of target (3pt made by each team) and of variables (last 5 games stats for each team)
    dates = ['_1', '_2', '_3', '_4', '_5', '_6', '_7', '_8', '_9', '_10', '_11', '_12', '_13', '_14', '_15']
    for date in dates:
        last_15_games = pd.merge(
            last_15_games, X,
            left_on=['date' + date, 'team'],
            right_on=['date', 'team'],
            how='left', suffixes=('', date)
        )

    cols = ['date', 'visitor', 'home', 'team', 'target'] + [tup[0] + tup[1] for tup in list(product(stats, dates))]

    last_15_games_unweighted = last_15_games[cols].copy()

    # Calculate mean for each stat over a team's last performance
    for stat in stats:
        last_15_games_unweighted[stat] = 0
        for date in dates:
            last_15_games_unweighted[stat] = last_15_games_unweighted[stat] + last_15_games_unweighted[stat + date]

        last_15_games_unweighted[stat] = last_15_games_unweighted[stat] / len(dates)

    # Calculate standard deviation for each stat over a team's performance
    for stat in stats:
        last_15_games_unweighted[stat + '_std'] = 0
        for date in dates:
            last_15_games_unweighted[stat + '_std'] = \
                last_15_games_unweighted[stat + '_std'] + \
                ((last_15_games_unweighted[stat + date] - last_15_games_unweighted[stat]) ** 2)

        last_15_games_unweighted[stat + '_std'] = last_15_games_unweighted[stat + '_std'] / len(dates)
        last_15_games_unweighted[stat + '_std'] = last_15_games_unweighted[stat + '_std'] ** .5

    # Feature engineer trends
    for stat in stats:
        last_15_games_unweighted[stat + '_trend'] = 0
        for date in dates[:10]:
            last_15_games_unweighted[stat + '_trend'] = \
                last_15_games_unweighted[stat + '_trend'] + \
                z_score(
                    last_15_games_unweighted[stat + date],
                    last_15_games_unweighted[stat],
                    last_15_games_unweighted[stat + '_std']
                ).fillna(0)

        last_15_games_unweighted[stat + '_trend'] = last_15_games_unweighted[stat + '_trend'] / len(dates[:10])

    last_15_games_unweighted = last_15_games_unweighted.groupby(['date', 'visitor', 'home']).aggregate(['mean', 'sum'])

    last_15_game_cols = [col
                         for col in last_15_games_unweighted.columns
                         if (col[0] == 'target' and col[1] == 'sum') or \
                         (col[0] in stats and col[1] == 'sum' and '_perc' not in col[0]) or \
                         (col[0] in stats and col[1] == 'mean' and '_perc' in col[0]) or \
                         ('_trend' in col[0] and col[1] == 'sum')]

    last_15_games_unweighted = last_15_games_unweighted[last_15_game_cols].dropna(axis=0)
    last_15_games_unweighted.columns = [col[0] for col in last_15_games_unweighted.columns]

    corr_df = pd.DataFrame()

    # Correlations for last 15 game stats vs 3pt made (unweighted)
    for col in last_15_games_unweighted:
        corr_p = pearsonr(last_15_games_unweighted['target'], last_15_games_unweighted[col])
        row = {'stat': col, 'corr': round(corr_p[0], 2), 'p-value': round(corr_p[1], 2)}
        corr_df = corr_df.append(row, ignore_index=True)

    # Statistically significant stats
    corr_df = corr_df[corr_df['p-value'] < .05].drop(['p-value'], axis=1).sort_values(['corr'], axis=0, ascending=False)

    stats = corr_df[corr_df['corr'].abs() >= .4]['stat']
    df = last_15_games_unweighted[stats]

    df.to_csv('backend/data/inputs/3p/game_totals.csv')


if __name__ == '__main__':
    preprocess()
