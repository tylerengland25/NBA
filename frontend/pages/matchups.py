import pandas as pd
import streamlit as st
from datetime import date


def app():
    # Header
    st.header(f'Matchups ({date.today()})')
    # Two columns for match up and line
    visitor, visitor_name, at, home, home_name = st.columns([15, 35, 10, 15, 35])

    # Today's games
    filename = 'C:\\Users\\tyler\\OneDrive\\Documents\\Python\\NBA\\backend\\predictions\\3p_predictions.csv'
    df = pd.read_csv(filename).drop(['Unnamed: 0'], axis=1)
    df['date'] = pd.to_datetime(df['date'])
    df = df[df['date'].dt.strftime('%Y-%m-%d') == str(date.today())]

    st.markdown("""
    <style>
    .big-font {
        font-size:20px !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Format matchups
    for index, row in df.iterrows():
        home_team = row['home']
        visitor_team = row['visitor']

        # Format visitor column
        visitor.image(
            f'frontend/logos/{visitor_team}.png',
            output_format='PNG',
            width=90
        )
        visitor_name.header('')
        visitor_name.markdown(f'<p class="big-font">{visitor_team}</p>', unsafe_allow_html=True)
        visitor_name.subheader('')

        # Format @ column
        at.header('')
        at.markdown(f'<p class="big-font">@</p>', unsafe_allow_html=True)
        at.subheader('')

        # Format home column
        home.image(
            f'frontend/logos/{home_team}.png',
            output_format='PNG',
            width=90
        )
        home_name.header('')
        home_name.markdown(f'<p class="big-font">{home_team}</p>', unsafe_allow_html=True)
        home_name.subheader('')
