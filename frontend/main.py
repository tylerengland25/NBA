import streamlit as st

# Custom imports
from multipage import MultiPage
from pages import schedule, rankings, picks, performance # import your pages here

# Create an instance of the app
app = MultiPage()

# Title of the main page
st.title("Sports Betting Application")

# Add all your applications (pages) here
app.add_page("Schedule", schedule.app)
app.add_page("Rankings", rankings.app)
app.add_page("Picks", picks.app)
app.add_page("Performance", performance.app)

# The main app
app.run()