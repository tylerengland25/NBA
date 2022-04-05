import numpy as np
import pandas as pd
import streamlit as st
import datetime


def load_data():
    predict_cols = ['date', 'visitor', 'home', 'random_forest', 'line', 'over', 'under']
    df = pd.read_csv('backend/predictions/3p_predictions.csv')[predict_cols]
    df['date'] = pd.to_datetime(df['date'])
    next_game = df['date'].max()

    df['pick'] = np.where(df['random_forest'] > df['line'], 'Over', 'Under')

    df['prediciton'] = df['random_forest']

    return df, next_game


def app():
    # Header
    st.header('Picks')

    # Predictions
    df, next_game = load_data()

    # Date
    date = st.date_input('Date: ', next_game)

    # Filter on date
    df = df[df['date'] == datetime.datetime(date.year, date.month, date.day)]

    # Rename
    df = df[['visitor', 'home', 'line', 'prediciton',  'pick']]
    df = df.rename(
        {'visitor': 'Visitor', 'home': 'Home', 'pick': 'Pick', 'prediction': 'Prediction', 'line': 'Line'},
        axis=1
    )
    df = df.dropna(axis=1, how='all')
    st.dataframe(df, 1000, 500)
