import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from io import StringIO

# Page config
st.set_page_config(page_title="Slavia Prague Fixtures & ELO", layout="wide")

def get_elo_data():
    """Fetch ELO data from the API"""
    response = requests.get('http://api.clubelo.com/SlaviaPraha')
    df = pd.read_csv(StringIO(response.text))
    latest_elo = df.iloc[-1]['Elo']
    return latest_elo, df

def get_fixtures():
    """Get fixtures data - placeholder for now"""
    return [
        {
            'date': '2024-02-18',
            'opponent': 'Sparta Prague',
            'competition': 'Czech Liga',
            'elo': 1705
        },
        {
            'date': '2024-02-25',
            'opponent': 'Viktoria Plzen',
            'competition': 'Czech Liga',
            'elo': 1622
        },
        {
            'date': '2024-03-03',
            'opponent': 'Banik Ostrava',
            'competition': 'Czech Liga',
            'elo': 1544
        }
    ]

# App title
st.title("Slavia Prague Fixtures & ELO Ratings")

# Get data
slavia_elo, elo_history = get_elo_data()
fixtures = get_fixtures()

# Display current ELO metrics
col1, col2 = st.columns(2)
with col1:
    st.metric("Slavia Prague Current ELO", f"{round(slavia_elo)}")
with col2:
    avg_opponent_elo = round(sum(f['elo'] for f in fixtures) / len(fixtures))
    st.metric("Average Opponent ELO", f"{avg_opponent_elo}")

# Create DataFrame for fixtures
fixtures_df = pd.DataFrame(fixtures)
fixtures_df['ELO Difference'] = round(slavia_elo - fixtures_df['elo'])

# Display fixtures table
st.subheader("Upcoming Fixtures")
st.dataframe(
    fixtures_df.rename(columns={
        'date': 'Date',
        'opponent': 'Opponent',
        'competition': 'Competition',
        'elo': 'Opponent ELO'
    }),
    hide_index=True
)

# Display ELO history chart
st.subheader("Slavia Prague ELO History")
st.line_chart(elo_history.set_index('From')['Elo'])