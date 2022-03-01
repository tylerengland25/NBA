import pandas as pd
import numpy as np
from itertools import product
from scipy.stats import pearsonr


def convert_mp(mp):
    if mp == '0' or mp == 0:
        return 0
    else:
        mins = int(mp.split(':')[0])
        secs = int(mp.split(':')[1]) / 60
        return mins + secs


# Return ten lastest dates team played
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


# Calculate z-score
def z_score(value, mean, std):
    return (value - mean) / std


# Calculate perc difference
def perc_diff(value, mean):
    return (value - mean) / mean


def preprocess():
    # Load data
    df = pd.read_csv('backend/data/details/advanced_details.csv').drop(['Unnamed: 0'], axis=1)
    shooting_df = pd.read_csv('backend/data/totals/game_totals.csv').drop(['Unnamed: 0'], axis=1)
    shooting_df = shooting_df[['date', 'visitor', 'home', 'team', '3p']]

    # Fill NaN
    df = df.fillna(0)

    # Convert 'date' column to Date object
    df['date'] = pd.to_datetime(df['date'])

    # Conver 'team' column to Team Name
    df['team'] = np.where(df['team'], df['home'], df['visitor'])

    # Convert 'minutes played' to float
    df['mp'] = df['mp'].apply(lambda x: convert_mp(x))

    # Set stats
    stats = ['ts_perc', 'efg_perc', '3par', 'ftr', 'orb_perc', 'drb_perc', 'trb_perc',
             'ast_perc', 'stl_perc', 'blk_perc', 'tov_perc', 'usg_perc', 'ortg', 'drtg', 'bpm', 'mp']

    # Team total stats
    teams_df = df.groupby(['date', 'visitor', 'home', 'team']).sum().reset_index()

    # Rename target variable
    shooting_df = shooting_df.rename({'3p': 'target'}, axis=1)

    # Convert 'date' column to Date object
    shooting_df['date'] = pd.to_datetime(shooting_df['date'])

    # Convert 'team' column to Team Name
    shooting_df['team'] = np.where(shooting_df['team'], shooting_df['home'], shooting_df['visitor'])

    # Starters total stats
    starters_df = df[df['starter'] == 1].groupby(['date', 'visitor', 'home', 'team']).aggregate(['sum', 'mean'])
    cols = [col for col in starters_df.columns
            if (col[0] == 'target' and col[1] == 'sum') or \
            (col[0] in stats and col[1] == 'mean' and '_perc' in col[0]) or \
            (col[0] in stats and col[1] == 'sum' and '_perc' not in col[0])]
    starters_df = starters_df[cols]
    starters_df.columns = [col[0] for col in starters_df.columns]
    starters_df = starters_df.reset_index()

    # Merge dataframes to have target variable
    starters_df = pd.merge(starters_df, shooting_df,
                           left_on=['date', 'visitor', 'home', 'team'], right_on=['date', 'visitor', 'home', 'team'],
                           how='left')

    # Bench total stats
    bench_df = df[df['starter'] == 0].groupby(['date', 'visitor', 'home', 'team']).aggregate(['sum', 'mean'])
    cols = [col for col in bench_df.columns
            if (col[0] == 'target' and col[1] == 'sum') or \
            (col[0] in stats and col[1] == 'mean' and '_perc' in col[0]) or \
            (col[0] in stats and col[1] == 'sum' and '_perc' not in col[0])]
    bench_df = bench_df[cols]
    bench_df.columns = [col[0] for col in bench_df.columns]
    bench_df = bench_df.reset_index()

    # Merge dataframes to have target variable
    bench_df = pd.merge(bench_df, shooting_df,
                        left_on=['date', 'visitor', 'home', 'team'], right_on=['date', 'visitor', 'home', 'team'],
                        how='left')

    teams_df['dates'] = teams_df.apply(lambda x: last_15_date(x.team, x.date, teams_df), axis=1)
    teams_df['date_1'], teams_df['date_2'] = teams_df['dates'].apply(lambda x: x[0]), teams_df['dates'].apply(
        lambda x: x[1])
    teams_df['date_3'], teams_df['date_4'] = teams_df['dates'].apply(lambda x: x[2]), teams_df['dates'].apply(
        lambda x: x[3])
    teams_df['date_5'], teams_df['date_6'] = teams_df['dates'].apply(lambda x: x[4]), teams_df['dates'].apply(
        lambda x: x[5])
    teams_df['date_7'], teams_df['date_8'] = teams_df['dates'].apply(lambda x: x[6]), teams_df['dates'].apply(
        lambda x: x[7])
    teams_df['date_9'], teams_df['date_10'] = teams_df['dates'].apply(lambda x: x[8]), teams_df['dates'].apply(
        lambda x: x[9])
    teams_df['date_11'], teams_df['date_12'] = teams_df['dates'].apply(lambda x: x[10]), teams_df['dates'].apply(
        lambda x: x[11])
    teams_df['date_13'], teams_df['date_14'] = teams_df['dates'].apply(lambda x: x[12]), teams_df['dates'].apply(
        lambda x: x[13])
    teams_df['date_15'] = teams_df['dates'].apply(lambda x: x[14])

    # Keep date columns in teams
    cols = [col for col in teams_df.columns
            if ('date_' in col) or \
            (col in ['date', 'visitor', 'home', 'team'])]
    teams_df = teams_df[cols]

    # Merge dates with starters
    starters_df = pd.merge(starters_df, teams_df,
                           left_on=['date', 'visitor', 'home', 'team'],
                           right_on=['date', 'visitor', 'home', 'team'],
                           how='left')

    # Merge dates with bench
    bench_df = pd.merge(bench_df, teams_df,
                        left_on=['date', 'visitor', 'home', 'team'],
                        right_on=['date', 'visitor', 'home', 'team'],
                        how='left')

    # Starters Analysis
    # X and y column names to merge on
    y_cols = starters_df.columns
    x_cols = ['date', 'team'] + stats

    last_15_games = starters_df[y_cols]
    X = starters_df[x_cols]

    # Dataframe of target (3pt made by each team) and of variables (last 5 games stats for each team)
    dates = ['_1', '_2', '_3', '_4', '_5', '_6', '_7', '_8', '_9', '_10', '_11', '_12', '_13', '_14', '_15']
    for date in dates:
        last_15_games = pd.merge(last_15_games, X, left_on=['date' + date, 'team'], right_on=['date', 'team'],
                                 how='left', suffixes=('', date))

    cols = ['date', 'visitor', 'home', 'team', 'target'] + \
           [tup[0] + tup[1] for tup in list(itertools.product(stats, dates))]

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
            last_15_games_unweighted[stat + '_std'] = last_15_games_unweighted[stat + '_std'] + \
                                                      ((last_15_games_unweighted[stat + date] -
                                                        last_15_games_unweighted[stat]) ** 2)

        last_15_games_unweighted[stat + '_std'] = last_15_games_unweighted[stat + '_std'] / len(dates)
        last_15_games_unweighted[stat + '_std'] = last_15_games_unweighted[stat + '_std'] ** .5

    # Feature engineer trends
    for stat in stats:
        last_15_games_unweighted[stat + '_trend'] = 0
        for date in dates[:10]:
            last_15_games_unweighted[stat + '_trend'] = last_15_games_unweighted[stat + '_trend'] + \
                                                        z_score(last_15_games_unweighted[stat + date],
                                                                last_15_games_unweighted[stat],
                                                                last_15_games_unweighted[stat + '_std']).fillna(0)

        last_15_games_unweighted[stat + '_trend'] = last_15_games_unweighted[stat + '_trend'] / len(dates[:10])

    last_15_games_unweighted = last_15_games_unweighted.groupby(['date', 'visitor', 'home']).aggregate(['mean', 'sum'])

    last_15_game_cols = [col
                         for col in last_15_games_unweighted.columns
                         if (col[0] == 'target' and col[1] == 'sum') or \
                         (col[0] in stats and col[1] == 'sum' and '_perc' not in col[0]) or \
                         (col[0] in stats and col[1] == 'mean' and '_perc' in col[0]) or \
                         ('_trend' in col[0] and col[1] == 'sum')]

    starters_15_games = last_15_games_unweighted[last_15_game_cols].dropna(axis=0).copy()
    starters_15_games.columns = [col[0] for col in starters_15_games.columns]

    corr_df = pd.DataFrame()

    # Correlations for last 15 game stats vs 3pt made (unweighted)
    for col in starters_15_games:
        corr_p = pearsonr(starters_15_games['target'], starters_15_games[col])
        row = {'stat': col, 'corr': round(corr_p[0], 2), 'p-value': round(corr_p[1], 2)}
        corr_df = corr_df.append(row, ignore_index=True)

    # Print statistically significant correlations
    starters_corr = corr_df[corr_df['p-value'] < .05].sort_values(['corr'], axis=0, ascending=False)

    # Bench Analysis
    # X and y column names to merge on
    y_cols = bench_df.columns
    x_cols = ['date', 'team'] + stats

    last_15_games = bench_df[y_cols]
    X = bench_df[x_cols]

    # Dataframe of target (3pt made by each team) and of variables (last 5 games stats for each team)
    dates = ['_1', '_2', '_3', '_4', '_5', '_6', '_7', '_8', '_9', '_10', '_11', '_12', '_13', '_14', '_15']
    for date in dates:
        last_15_games = pd.merge(last_15_games, X, left_on=['date' + date, 'team'], right_on=['date', 'team'],
                                 how='left', suffixes=('', date))



if __name__ == '__main__':
    preprocess()
