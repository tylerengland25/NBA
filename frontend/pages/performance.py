import pandas as pd
import streamlit as st
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt


def load_data():
    # Load data
    totals_cols = ['date', 'visitor', 'home', '3p']
    totals_df = pd.read_csv('backend/data/totals/game_totals.csv').drop(['Unnamed: 0'], axis=1)[totals_cols]
    predict_df = pd.read_csv('backend/predictions/3p_predictions.csv').drop(['Unnamed: 0'], axis=1)

    # Convert date to datetime
    totals_df['date'] = pd.to_datetime(totals_df['date'])
    predict_df['date'] = pd.to_datetime(predict_df['date'])

    # Total 3pt by both teams
    totals_df = totals_df.groupby(['date', 'visitor', 'home']).sum()

    # Merge dataframes
    df = pd.merge(
        predict_df,
        totals_df,
        left_on=['date', 'visitor', 'home'],
        right_on=['date', 'visitor', 'home'],
        how='left'
    )
    df = df.drop_duplicates(['date', 'visitor', 'home']).dropna(axis=0)

    df = df[df['3p'] > 0]

    df['random_forest_predict'] = np.where(df['random_forest'] > df['line'], 'o', 'u')

    # Compute if model predicted correctly
    df['random_forest_hit'] = \
        ((df['3p'] > df['line']) & (df['random_forest'] > df['line'])) | \
        ((df['3p'] < df['line']) & (df['random_forest'] < df['line']))

    # Compute models profit per bet
    df['random_forest_potential_profit'] = np.where(
        df['random_forest'] > df['line'], 
        df['over'].apply(int), 
        df['under'].apply(int)
    )

    df['random_forest_potential_profit'] = np.where(
        df['random_forest_potential_profit'] > 0, 
        df['random_forest_potential_profit'] / 100 * df['random_forest_unit'],
        -100 / df['random_forest_potential_profit'] * df['random_forest_unit']
    )

    df['random_forest_profit'] = np.where(df['random_forest_hit'], df['random_forest_potential_profit'], -1 * df['random_forest_unit'])

    # Compute accumulative profit overtime
    df['random_forest_accumulative_profit'] = df['random_forest_profit'].cumsum()

    return df


def prediction_data():
    predict_cols = ['date', 'visitor', 'home', 'random_forest', 'random_forest_unit', 'line', 'over', 'under']
    predict_df = pd.read_csv('backend/predictions/3p_predictions.csv')[predict_cols]
    predict_df['date'] = pd.to_datetime(predict_df['date'])

    totals_cols = ['date', 'visitor', 'home', '3p']
    totals_df = pd.read_csv('backend/data/totals/game_totals.csv')[totals_cols]
    totals_df = totals_df.groupby(['date', 'visitor', 'home']).aggregate('sum').reset_index()
    totals_df['date'] = pd.to_datetime(totals_df['date'])

    df = pd.merge(predict_df, totals_df, left_on=['date', 'visitor', 'home'], right_on=['date', 'visitor', 'home'])

    df['pick'] = np.where(df['random_forest'] > df['line'], 'Over', 'Under')
    df['potential_payout'] = np.where(
        df['pick'] == 'Over',
        df['over'].apply(lambda x: float(x) if x != np.NaN else x),
        df['under'].apply(lambda x: float(x) if x != np.NaN else x)
    )

    df['potential_payout'] = np.where(
        df['potential_payout'] > 0,
        df['potential_payout'] / 100 * df['random_forest_unit'],
        -100 / df['potential_payout'] * df['random_forest_unit']
    )

    df['outcome'] = np.where(df['3p'] > df['line'], 'Over', 'Under')
    df['outcome'] = np.where(df['outcome'] == df['pick'], 'HIT', 'BUST')
    df['outcome'] = np.where(df['3p'] == 0, None, df['outcome'])
    df['payout'] = np.where(df['outcome'] == 'HIT', df['potential_payout'], -1 * df['random_forest_unit'])
    df['payout'] = np.where(df['outcome'].isna(), None, df['payout'])
    df['date'] = df['date'].dt.strftime('%Y-%m-%d')

    return df


def graph(df):
    # Seaborn formatting
    sns.set(rc={"figure.figsize": (15, 10)})
    fig = plt.figure()
    sns.lineplot(
        data=df.groupby(['date']).sum(),
        x='date',
        y=df.groupby(['date']).sum()[f'random_forest_profit'].cumsum(),
        color='green'
    )
    plt.xlabel('Date', fontsize=20)
    plt.ylabel('Units', fontsize=20)
    plt.xticks(fontsize=15, rotation=25)
    plt.yticks(fontsize=15)

    return fig


def app():
    # Header
    st.header('Performance Page')

    # Load data
    df = load_data()

    # Calculate performance
    profit = df['random_forest_profit'].sum()
    correct = df[df['random_forest_hit'] == True]['random_forest_hit'].count()
    wrong = df[df['random_forest_hit'] == False]['random_forest_hit'].count()

    # Format
    cols = st.columns(3)
    profit_delta = round(df.groupby('date').sum().iloc[-1, :]['random_forest_profit'], 2)
    correct_delta = \
        df[(df['date'] < df['date'].max()) & (df['random_forest_hit'] == True)]['random_forest_hit'].count()
    wrong_delta = \
        df[(df['date'] < df['date'].max()) & (df['random_forest_hit'] == False)]['random_forest_hit'].count()
    accuracy_delta = round((correct_delta / (correct_delta + wrong_delta)) * 100)

    cols[0].metric(
        label=f'Profit',
        value=f'{round(profit, 2)} Units',
        delta=profit_delta
    )
    cols[1].metric(
        label=f'Accuracy',
        value=f'{round((correct / (correct + wrong)) * 100)}%',
        delta=f'{round(((correct / (correct + wrong)) * 100) - accuracy_delta, 2)}'
    )
    cols[2].metric(label=f'Record', value=f'{correct} - {wrong}')

    # Graph
    fig = graph(df)
    st.pyplot(fig)

    # History
    st.subheader('History')
    df = prediction_data()
    df = df[['date', 'home', 'visitor', 'pick', 'line', 'outcome', 'payout']]
    df = df.rename(
        {'date': 'Date', 'home': 'Home', 'visitor': 'Visitor', 'pick': 'Pick',
         'line': 'Line', 'outcome': 'Outcome', 'payout': 'Payout'},
        axis=1
    )
    st.dataframe(df, 2000, 1000)

