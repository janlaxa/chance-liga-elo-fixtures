import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from io import StringIO

# Page config
st.set_page_config(page_title="Czech Football Clubs ELO", layout="wide")

club_average_opponent_elo = pd.read_csv("data/processed/club_average_opponent_elo.csv")

# App title
st.title("Czech Football Clubs ELO Ratings")

# Display stats
st.subheader("Current ELO Ratings")
# Custom CSS for tooltip
st.markdown(
    """
    <style>
    .tooltip {
        position: relative;
        display: inline-block;
        cursor: pointer;
    }
    
    .tooltip .tooltiptext {
        visibility: hidden;
        width: 120px;
        background-color: black;
        color: #fff;
        text-align: center;
        border-radius: 5px;
        padding: 5px;
        position: absolute;
        z-index: 1;
        bottom: 100%;
        left: 50%;
        margin-left: -60px;
        opacity: 0;
        transition: opacity 0.3s;
    }
    
    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Add tooltip to club names

club_average_opponent_elo["club_name"] = club_average_opponent_elo["club_name"].apply(lambda x: f'<div class="tooltip">{x}<span class="tooltiptext">{x}</span></div>')

# Display table with tooltips
st.write(club_average_opponent_elo.to_html(escape=False), unsafe_allow_html=True)