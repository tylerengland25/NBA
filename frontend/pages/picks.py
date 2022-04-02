import numpy as np
import pandas as pd
import streamlit as st


def load_data():
    predict_cols = ['date', 'visitor', 'home', 'random_forest', 'line', 'over', 'under']
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
        df['over'],
        df['under']
    )

    df['potential_payout'] = np.where(
        df['potential_payout'] > 0,
        df['potential_payout'] / 100,
        -100 / df['potential_payout']
    )

    df['outcome'] = np.where(df['3p'] > df['line'], 'Over', 'Under')
    df['outcome'] = np.where(df['outcome'] == df['pick'], 'HIT', 'BUST')
    df['outcome'] = np.where(df['3p'] == 0, None, df['outcome'])
    df['payout'] = np.where(df['outcome'] == 'HIT', df['potential_payout'], -1)
    df['payout'] = np.where(df['outcome'].isna(), None, df['payout'])
    df['date'] = df['date'].dt.strftime('%Y-%m-%d')

    return df


def app():
    # Header
    st.header('Picks')

    # Date
    date = st.date_input('Date: ')

    # Predictions
    df = load_data()

    # Filter on date
    df = df[df['date'] == str(date)]

    # Rename
    df = df[['visitor', 'home', 'line', 'pick', 'outcome', 'payout']]
    df = df.rename(
        {'visitor': 'Visitor', 'home': 'Home', 'pick': 'Pick', 'line':
            'Line', 'outcome': 'Outcome', 'payout': 'Payout'},
        axis=1
    )
    df = df.dropna(axis=1, how='all')
    st.dataframe(df, 1000, 500)
