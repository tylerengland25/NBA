import datetime

import pandas as pd
import numpy as np


def convert_mp(mp):
    if mp == '0' or mp == 0:
        return 0
    else:
        mins = int(mp.split(':')[0])
        secs = int(mp.split(':')[1]) / 60
        return mins + secs


def load_data():
    df = pd.read_csv('backend/data/details/game_details.csv').drop(['Unnamed: 0'], axis=1)
    shooting_df = pd.read_csv('backend/data/totals/game_totals.csv').drop(['Unnamed: 0'], axis=1)
    shooting_df = shooting_df[['date', 'visitor', 'home', 'team', '3p']]

    # Set stats
    stats = ['fg', 'fga', '3p', '3pa', 'ft', 'fta',
             'orb', 'drb', 'trb', 'ast', 'stl', 'blk',
             'tov', 'pf', 'pts', 'plus_minus', 'mp']

    # Fill NaN
    df = df.fillna(0)

    # Convert 'date' column to Date object
    df['date'] = pd.to_datetime(df['date'])

    # Convert 'team' column to Team Name
    df['team'] = np.where(df['team'], df['home'], df['visitor'])

    # Convert 'minutes played' to float
    df['mp'] = df['mp'].apply(lambda x: convert_mp(x))

    # Team total stats
    teams_df = df.groupby(['date', 'visitor', 'home', 'team']).sum().reset_index()

    # Starters total stats
    starters_df = df[df['starter'] == 1].groupby(['date', 'visitor', 'home', 'team']).sum()
    starters_df = starters_df[stats]
    starters_df = starters_df.reset_index()

    # Bench total stats
    bench_df = df[df['starter'] == 0].groupby(['date', 'visitor', 'home', 'team']).sum()
    bench_df = bench_df[stats]
    bench_df = bench_df.reset_index()

    # Merge in opponents (see team defensive stats)
    starters_df = pd.merge(
        starters_df,
        starters_df,
        left_on=['date', 'visitor', 'home'],
        right_on=['date', 'visitor', 'home'],
        suffixes=('', '_opp'),
        how='left')

    starters_df = starters_df[starters_df['team'] != starters_df['team_opp']]

    bench_df = pd.merge(
        bench_df,
        bench_df,
        left_on=['date', 'visitor', 'home'],
        right_on=['date', 'visitor', 'home'],
        suffixes=('', '_opp'),
        how='left')

    bench_df = bench_df[bench_df['team'] != bench_df['team_opp']]

    return teams_df, starters_df, bench_df


def load_next_slate(total_df):
    df = pd.read_csv('backend/data/schedules/2021.csv')
    df['date'] = pd.to_datetime(df['date'])

    next_date = set(df['date'].unique()).difference(set(total_df['date'].unique()))
    next_date = pd.Series(list(next_date)).sort_values(ascending=True).iloc[0]

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


def merge_last_15(starters_df, bench_df, next_slate):
    # Set stats
    stats = ['fg', 'fga', '3p', '3pa', 'ft', 'fta',
             'orb', 'drb', 'trb', 'ast', 'stl', 'blk',
             'tov', 'pf', 'pts', 'plus_minus', 'mp']
    opp_stats = [stat + '_opp' for stat in stats]
    stats = stats + opp_stats

    # X and y column names to merge on
    x_cols = ['date', 'team'] + stats

    # Keep date columns in teams
    cols = [col for col in next_slate.columns
            if ('date_' in col) or \
            (col in ['date', 'visitor', 'home', 'team'])]
    next_slate = next_slate[cols]

    # Merge dates with starters
    next_slate_starters = pd.merge(next_slate, starters_df,
                                   left_on=['date', 'visitor', 'home', 'team'],
                                   right_on=['date', 'visitor', 'home', 'team'],
                                   how='left')

    # Merge dates with bench
    next_slate_bench = pd.merge(next_slate, bench_df,
                                left_on=['date', 'visitor', 'home', 'team'],
                                right_on=['date', 'visitor', 'home', 'team'],
                                how='left')

    # Dataframe of target (3pt made by each team) and of variables (last 5 games stats for each team)
    dates = ['_1', '_2', '_3', '_4', '_5', '_6', '_7', '_8', '_9', '_10', '_11', '_12', '_13', '_14', '_15']
    for date in dates:
        next_slate_starters = pd.merge(
            next_slate_starters,
            starters_df[x_cols],
            left_on=['date' + date, 'team'],
            right_on=['date', 'team'],
            how='left',
            suffixes=('', date)
        )

        next_slate_bench = pd.merge(
            next_slate_bench,
            bench_df[x_cols],
            left_on=['date' + date, 'team'],
            right_on=['date', 'team'],
            how='left',
            suffixes=('', date)
        )

    return next_slate_starters, next_slate_bench


def starters_preprocess(starters_df):
    # Set stats
    stats = ['fg', 'fga', '3p', '3pa', 'ft', 'fta',
             'orb', 'drb', 'trb', 'ast', 'stl', 'blk',
             'tov', 'pf', 'pts', 'plus_minus', 'mp']
    opp_stats = [stat + '_opp' for stat in stats]
    stats = stats + opp_stats

    dates = ['_1', '_2', '_3', '_4', '_5', '_6', '_7', '_8', '_9', '_10', '_11', '_12', '_13', '_14', '_15']

    last_15 = starters_df.copy()

    # Calculate mean for each stat over a team's last performance
    for stat in stats:
        last_15[stat + '_last_15'] = 0
        last_15[stat + '_last_3'] = 0
        last_15[stat + '_last_1'] = 0

        for date in dates:
            # Last 15 games
            last_15[stat + '_last_15'] = last_15[stat + '_last_15'] + last_15[stat + date]

            # Last 3 games
            if date in ['_1', '_2', '_3']:
                last_15[stat + '_last_3'] = last_15[stat + '_last_3'] + last_15[stat + date]

            # Last game
            if date in ['_1']:
                last_15[stat + '_last_1'] = last_15[stat + '_last_1'] + last_15[stat + date]

        last_15[stat + '_last_15'] = last_15[stat + '_last_15'] / 15
        last_15[stat + '_last_3'] = last_15[stat + '_last_3'] / 3

    # Calculate difference between last 15 games, 3 games and last game
    for stat in stats:
        last_15[stat + '_trend_3'] = last_15[stat + '_last_15'] - last_15[stat + '_last_3']
        last_15[stat + '_trend_1'] = last_15[stat + '_last_15'] - last_15[stat + '_last_1']

    # Sum stats for opposing teams for each game
    last_15 = last_15.groupby(['date', 'visitor', 'home']).sum()

    # Keep columns
    stats_15 = [stat + '_last_15' for stat in stats]
    stats_3 = [stat + '_last_3' for stat in stats]
    stats_1 = [stat + '_last_1' for stat in stats]
    trend_3 = [stat + '_trend_3' for stat in stats]
    trend_1 = [stat + '_trend_1' for stat in stats]
    last_15 = last_15[stats_1 + stats_3 + stats_15 + trend_1 + trend_3]

    # Calculate percentages
    last_15['fg_perc_last_15'] = last_15['fg_last_15'] / last_15['fga_last_15']
    last_15['fg_perc_opp_last_15'] = last_15['fg_opp_last_15'] / last_15['fga_opp_last_15']

    last_15['3p_perc_last_15'] = last_15['3p_last_15'] / last_15['3pa_last_15']
    last_15['3p_perc_opp_last_15'] = last_15['3p_opp_last_15'] / last_15['3pa_opp_last_15']

    last_15['ft_perc_last_15'] = last_15['ft_last_15'] / last_15['fta_last_15']
    last_15['ft_perc_opp_last_15'] = last_15['ft_opp_last_15'] / last_15['fta_opp_last_15']

    # Calculate advanced stats
    last_15['ts_perc_last_15'] = last_15['pts_last_15'] / (2 * (last_15['fga_last_15'] + .44 * last_15['fta_last_15']))
    last_15['ts_perc_opp_last_15'] = last_15['pts_opp_last_15'] / (
            2 * (last_15['fga_opp_last_15'] + .44 * last_15['fta_opp_last_15']))

    last_15['efg_perc_last_15'] = (last_15['fg_last_15'] + (.5 * last_15['3p_last_15'])) / last_15['fga_last_15']
    last_15['efg_perc_opp_last_15'] = (last_15['fg_opp_last_15'] + (.5 * last_15['3p_opp_last_15'])) / last_15[
        'fga_opp_last_15']

    last_15['3par_last_15'] = last_15['3pa_last_15'] / last_15['fga_last_15']
    last_15['3par_opp_last_15'] = last_15['3pa_opp_last_15'] / last_15['fga_opp_last_15']

    last_15['ftr_last_15'] = last_15['fta_last_15'] / last_15['fga_last_15']
    last_15['ftr_opp_last_15'] = last_15['fta_opp_last_15'] / last_15['fga_opp_last_15']

    last_15['orb_perc_last_15'] = last_15['orb_last_15'] / (last_15['orb_last_15'] + last_15['drb_opp_last_15'])
    last_15['orb_perc_opp_last_15'] = last_15['orb_opp_last_15'] / (last_15['orb_opp_last_15'] + last_15['drb_last_15'])

    last_15['drb_perc_last_15'] = last_15['drb_last_15'] / (last_15['drb_last_15'] + last_15['orb_opp_last_15'])
    last_15['drb_perc_opp_last_15'] = last_15['drb_opp_last_15'] / (last_15['drb_opp_last_15'] + last_15['orb_last_15'])

    last_15['trb_perc_last_15'] = last_15['trb_last_15'] / (last_15['trb_last_15'] + last_15['trb_opp_last_15'])
    last_15['trb_perc_opp_last_15'] = last_15['trb_opp_last_15'] / (last_15['trb_opp_last_15'] + last_15['trb_last_15'])

    last_15['ast_perc_last_15'] = last_15['ast_last_15'] / last_15['fg_last_15']
    last_15['ast_perc_opp_last_15'] = last_15['ast_opp_last_15'] / last_15['fg_opp_last_15']

    starters_15_games = last_15.dropna(axis=0).copy()

    return starters_15_games


def bench_preprocess(bench_df):
    # Set stats
    stats = ['fg', 'fga', '3p', '3pa', 'ft', 'fta',
             'orb', 'drb', 'trb', 'ast', 'stl', 'blk',
             'tov', 'pf', 'pts', 'plus_minus', 'mp']
    opp_stats = [stat + '_opp' for stat in stats]
    stats = stats + opp_stats

    dates = ['_1', '_2', '_3', '_4', '_5', '_6', '_7', '_8', '_9', '_10', '_11', '_12', '_13', '_14', '_15']

    last_15 = bench_df.copy()

    # Calculate mean for each stat over a team's last performance
    for stat in stats:
        last_15[stat + '_last_15'] = 0
        last_15[stat + '_last_3'] = 0
        last_15[stat + '_last_1'] = 0

        for date in dates:
            # Last 15 games
            last_15[stat + '_last_15'] = last_15[stat + '_last_15'] + last_15[stat + date]

            # Last 3 games
            if date in ['_1', '_2', '_3']:
                last_15[stat + '_last_3'] = last_15[stat + '_last_3'] + last_15[stat + date]

            # Last game
            if date in ['_1']:
                last_15[stat + '_last_1'] = last_15[stat + '_last_1'] + last_15[stat + date]

        last_15[stat + '_last_15'] = last_15[stat + '_last_15'] / 15
        last_15[stat + '_last_3'] = last_15[stat + '_last_3'] / 3

    # Calculate difference between last 15 games, 3 games and last game
    for stat in stats:
        last_15[stat + '_trend_3'] = last_15[stat + '_last_15'] - last_15[stat + '_last_3']
        last_15[stat + '_trend_1'] = last_15[stat + '_last_15'] - last_15[stat + '_last_1']

    # Sum stats for opposing teams for each game
    last_15 = last_15.groupby(['date', 'visitor', 'home']).sum()

    # Keep columns
    stats_15 = [stat + '_last_15' for stat in stats]
    stats_3 = [stat + '_last_3' for stat in stats]
    stats_1 = [stat + '_last_1' for stat in stats]
    trend_3 = [stat + '_trend_3' for stat in stats]
    trend_1 = [stat + '_trend_1' for stat in stats]
    last_15 = last_15[stats_1 + stats_3 + stats_15 + trend_1 + trend_3]

    # Calculate percentages
    last_15['fg_perc_last_15'] = last_15['fg_last_15'] / last_15['fga_last_15']
    last_15['fg_perc_opp_last_15'] = last_15['fg_opp_last_15'] / last_15['fga_opp_last_15']

    last_15['3p_perc_last_15'] = last_15['3p_last_15'] / last_15['3pa_last_15']
    last_15['3p_perc_opp_last_15'] = last_15['3p_opp_last_15'] / last_15['3pa_opp_last_15']

    last_15['ft_perc_last_15'] = last_15['ft_last_15'] / last_15['fta_last_15']
    last_15['ft_perc_opp_last_15'] = last_15['ft_opp_last_15'] / last_15['fta_opp_last_15']

    # Calculate advanced stats
    last_15['ts_perc_last_15'] = last_15['pts_last_15'] / (2 * (last_15['fga_last_15'] + .44 * last_15['fta_last_15']))
    last_15['ts_perc_opp_last_15'] = last_15['pts_opp_last_15'] / (
            2 * (last_15['fga_opp_last_15'] + .44 * last_15['fta_opp_last_15']))

    last_15['efg_perc_last_15'] = (last_15['fg_last_15'] + (.5 * last_15['3p_last_15'])) / last_15['fga_last_15']
    last_15['efg_perc_opp_last_15'] = (last_15['fg_opp_last_15'] + (.5 * last_15['3p_opp_last_15'])) / last_15[
        'fga_opp_last_15']

    last_15['3par_last_15'] = last_15['3pa_last_15'] / last_15['fga_last_15']
    last_15['3par_opp_last_15'] = last_15['3pa_opp_last_15'] / last_15['fga_opp_last_15']

    last_15['ftr_last_15'] = last_15['fta_last_15'] / last_15['fga_last_15']
    last_15['ftr_opp_last_15'] = last_15['fta_opp_last_15'] / last_15['fga_opp_last_15']

    last_15['orb_perc_last_15'] = last_15['orb_last_15'] / (last_15['orb_last_15'] + last_15['drb_opp_last_15'])
    last_15['orb_perc_opp_last_15'] = last_15['orb_opp_last_15'] / (last_15['orb_opp_last_15'] + last_15['drb_last_15'])

    last_15['drb_perc_last_15'] = last_15['drb_last_15'] / (last_15['drb_last_15'] + last_15['orb_opp_last_15'])
    last_15['drb_perc_opp_last_15'] = last_15['drb_opp_last_15'] / (last_15['drb_opp_last_15'] + last_15['orb_last_15'])

    last_15['trb_perc_last_15'] = last_15['trb_last_15'] / (last_15['trb_last_15'] + last_15['trb_opp_last_15'])
    last_15['trb_perc_opp_last_15'] = last_15['trb_opp_last_15'] / (last_15['trb_opp_last_15'] + last_15['trb_last_15'])

    last_15['ast_perc_last_15'] = last_15['ast_last_15'] / last_15['fg_last_15']
    last_15['ast_perc_opp_last_15'] = last_15['ast_opp_last_15'] / last_15['fg_opp_last_15']

    bench_15_games = last_15.dropna(axis=0).copy()

    return bench_15_games


def input_data(starters_df, bench_df):
    cols = [
        '3par_last_15_starters', '3pa_last_15_starters', '3p_last_15_starters', '3pa_opp_last_15_starters',
        '3par_opp_last_15_starters', '3pa_last_3_starters', '3p_opp_last_15_starters', '3pa_last_1_starters',
        '3pa_opp_last_3_starters', '3p_last_3_starters', '3pa_opp_last_15_bench', '3par_opp_last_15_bench',
        '3pa_last_15_bench', '3par_last_15_bench', '3p_opp_last_15_bench', '3p_last_15_bench'
    ]

    df = pd.merge(
        starters_df, bench_df,
        left_on=['date', 'visitor', 'home'],
        right_on=['date', 'visitor', 'home'],
        how='outer', suffixes=('_starters', '_bench')
    )

    df = df[cols]
    df = df.rename(
        {
            '3pa_last_3_starters': '3pa_last_3',
            '3pa_last_1_starters': '3pa_last_1',
            '3pa_opp_last_3_starters': '3pa_opp_last_3',
            '3p_last_3_starters': '3p_last_3'
        },
        axis=1
    )
    next_slate = df.reset_index()
    next_slate['date'] = next_slate['date'].apply(lambda x: datetime.date(x.year, x.month, x.day))

    return next_slate


def merge_input_data(next_slate):
    inputs = pd.read_csv('backend/data/inputs/3p/game_details.csv').drop(['Unnamed: 0'], axis=1)

    inputs = pd.concat(
        [inputs, next_slate]
    )
    inputs['date'] = pd.to_datetime(inputs['date'])
    inputs['date'] = inputs['date'].apply(lambda x: datetime.date(x.year, x.month, x.day))

    inputs = inputs.drop_duplicates(['date', 'visitor', 'home'], keep='last').reset_index().drop(['index'], axis=1)

    inputs.to_csv('backend/data/inputs/3p/game_details.csv')


def main():
    # Load totals
    teams_df, starters_df, bench_df = load_data()

    # Load schedule for next games (not scraped games)
    next_slate = load_next_slate(teams_df)

    # Last 15 dates of next slate
    next_slate = next_slate_last_15(next_slate, teams_df)

    # Merge last 15 games of data
    starters_df, bench_df = merge_last_15(starters_df, bench_df, next_slate)

    # Compute averages
    starters_df = starters_preprocess(starters_df)
    bench_df = bench_preprocess(bench_df)

    # Input dataframe
    next_slate = input_data(starters_df, bench_df)

    # Merge next_slate into input data
    merge_input_data(next_slate)


if __name__ == '__main__':
    main()
