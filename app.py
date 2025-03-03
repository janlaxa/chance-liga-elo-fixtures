import streamlit as st
import pandas as pd
import numpy as np
import datetime
import os
import plotly.graph_objects as go
import plotly.express as px
import base64
from io import BytesIO
from PIL import Image

from data.raw.club_mapping import club_mapping
from modules.get_scoreboard_name import get_scoreboard_name
from modules.get_elo_diff_bar_chart import get_elo_diff_bar_chart
from modules.get_elo_fixtures_bar_chart import get_elo_fixtures_bar_chart

# Page config
st.set_page_config(page_title="Czech Football Clubs ELO", layout="wide")

today = datetime.datetime.today()
club_average_opponent_elo = pd.read_csv("data/processed/club_average_opponent_elo.csv")
club_average_opponent_elo["scoreboard"] = club_average_opponent_elo["club_name"].apply(lambda x: get_scoreboard_name(x, club_mapping))

fixtures = pd.read_csv("data/processed/fixtures.csv")
club_elo = pd.read_csv("data/processed/club_elo.csv")

fixtures["home_team_elo"] = fixtures["home_team_id"].map(club_elo.set_index("club_id")["elo_rating"])
fixtures["away_team_elo"] = fixtures["away_team_id"].map(club_elo.set_index("club_id")["elo_rating"])
fixtures["event_date"] = pd.to_datetime(fixtures["event_date"])

st.title("Chance Liga")
st.subheader("Kdo má nejtěžší los?")
club_average_opponent_elo = club_average_opponent_elo.sort_values(by="average_opponent_elo")

# Create figure
fig = go.Figure()

# Add the club's own ELO rating (wider, gray bars)
fig.add_trace(go.Bar(
    y=club_average_opponent_elo["club_name"],
    x=club_average_opponent_elo["club_elo"],
    name="Club ELO",
    orientation='h',
    marker=dict(color='rgba(0,0,0,0.2)'),
    width=0.7  # Wider bars
))

# Add the average opponent ELO (thinner, colored bars)
fig.add_trace(go.Bar(
    y=club_average_opponent_elo["club_name"],
    x=club_average_opponent_elo["average_opponent_elo"],
    name="Average Opponent ELO",
    orientation='h',
    marker=dict(color='blue'),
    width=0.5,  # Thinner bars
    text=club_average_opponent_elo["average_opponent_elo"].astype(int),
    textfont = dict(color = 'black', size = 10),
    textposition='outside'
))

# Add club logos
for idx, row in club_average_opponent_elo.iterrows():
    club_info = next((item for item in club_mapping.values() if item["club_name"] == row["club_name"]), None)
    if club_info:
        fig.add_layout_image(
            dict(
                source=Image.open(club_info["club_logo"]),
                xref="paper", yref="y",
                x=0, y=row["club_name"],
                sizex=0.1, sizey=1,
                xanchor="right", yanchor="middle"
            )
        )

# Layout adjustments
fig.update_layout(
    barmode='overlay',  # Overlapping bars
    width=300,  # Adjust width as needed
    height=600,  # Adjust height as needed
    yaxis=dict(
        tickmode='array',
        tickvals=club_average_opponent_elo["club_name"],
        ticktext=club_average_opponent_elo["scoreboard"],
        tickfont=dict(size=10),
        tickangle=0,
        automargin=True,
        ticklabelposition="outside",
        ticklen=20,
        tickcolor='rgba(0,0,0,0)',
    ),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=-0.2,
        xanchor="center",
        x=0.5
    ),
    margin=dict(l=100, r=20, t=20, b=100)  # Adjust margins as needed
)

# Create figure
fig1 = go.Figure()

# Add the club's own ELO rating (wider, gray bars)
fig1.add_trace(go.Bar(
    y=club_average_opponent_elo["club_name"],
    x=club_average_opponent_elo["club_elo"],
    name="Club ELO",
    orientation='h',
    marker=dict(color='rgba(0,0,0,0.2)'),
    width=0.7  # Wider bars
))

# Add the average opponent ELO (thinner, colored bars)
fig1.add_trace(go.Bar(
    y=club_average_opponent_elo["club_name"],
    x=club_average_opponent_elo["average_home_opponent_elo"],
    name="Average Opponent ELO",
    orientation='h',
    marker=dict(color='purple'),
    width=0.5,  # Thinner bars
    text=club_average_opponent_elo["average_home_opponent_elo"].astype(int),
    textfont = dict(color = 'black', size = 10),
    textposition='outside'
))

# Add club logos
for idx, row in club_average_opponent_elo.iterrows():
    club_info = next((item for item in club_mapping.values() if item["club_name"] == row["club_name"]), None)
    if club_info:
        fig1.add_layout_image(
            dict(
                source=Image.open(club_info["club_logo"]),
                xref="paper", yref="y",
                x=0, y=row["club_name"],
                sizex=0.1, sizey=1,
                xanchor="right", yanchor="middle"
            )
        )

# Layout adjustments
fig1.update_layout(
    barmode='overlay',  # Overlapping bars
    width=300,  # Adjust width as needed
    height=600,  # Adjust height as needed
    yaxis=dict(
        tickmode='array',
        tickvals=club_average_opponent_elo["club_name"],
        ticktext=club_average_opponent_elo["scoreboard"],
        tickfont=dict(size=10),
        tickangle=0,
        automargin=True,
        ticklabelposition="outside",
        ticklen=20,
        tickcolor='rgba(0,0,0,0)',
    ),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=-0.2,
        xanchor="center",
        x=0.5
    ),
    margin=dict(l=100, r=20, t=20, b=100)  # Adjust margins as needed
)

fig2 = go.Figure()

# Add the club's own ELO rating (wider, gray bars)
fig2.add_trace(go.Bar(
    y=club_average_opponent_elo["club_name"],
    x=club_average_opponent_elo["club_elo"],
    name="Club ELO",
    orientation='h',
    marker=dict(color='rgba(0,0,0,0.2)'),
    width=0.7  # Wider bars
))

# Add the average opponent ELO (thinner, colored bars)
fig2.add_trace(go.Bar(
    y=club_average_opponent_elo["club_name"],
    x=club_average_opponent_elo["average_away_opponent_elo"],
    name="Average Opponent ELO",
    orientation='h',
    marker=dict(color='purple'),
    width=0.5,  # Thinner bars
    text=club_average_opponent_elo["average_away_opponent_elo"].astype(int),
    textfont = dict(color = 'black', size = 10),
    textposition='outside'
))

# Add club logos
for idx, row in club_average_opponent_elo.iterrows():
    club_info = next((item for item in club_mapping.values() if item["club_name"] == row["club_name"]), None)
    if club_info:
        fig2.add_layout_image(
            dict(
                source=Image.open(club_info["club_logo"]),
                xref="paper", yref="y",
                x=0, y=row["club_name"],
                sizex=0.1, sizey=1,
                xanchor="right", yanchor="middle"
            )
        )

# Layout adjustments
fig2.update_layout(
    barmode='overlay',  # Overlapping bars
    width=300,  # Adjust width as needed
    height=600,  # Adjust height as needed
    yaxis=dict(
        tickmode='array',
        tickvals=club_average_opponent_elo["club_name"],
        ticktext=club_average_opponent_elo["scoreboard"],
        tickfont=dict(size=10),
        tickangle=0,
        automargin=True,
        ticklabelposition="outside",
        ticklen=20,
        tickcolor='rgba(0,0,0,0)',
    ),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=-0.2,
        xanchor="center",
        x=0.5
    ),
    margin=dict(l=100, r=20, t=20, b=100)  # Adjust margins as needed
)


cols = st.columns(3)
with cols[0]:
    st.plotly_chart(fig, use_container_width=False, width=400)
with cols[1]:
    st.plotly_chart(fig1, use_container_width=False, width=400)
with cols[2]:
    st.plotly_chart(fig2, use_container_width=False, width=400)









scoreboard_logo_list = [(k, v["scoreboard"], v["club_logo"]) for k, v in club_mapping.items()]

# Initialize session state for selected club
if "selected_club_ids" not in st.session_state:
    st.session_state["selected_club_ids"] = []

st.markdown("""
<style>
    [data-testid=stSidebar] {
        background-color: #AEFF00;
    }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    "## Vyběr klubů"
    "Kliknutním zobrazíte/skryjete nadcházející zápasy"
    for club_id, scoreboard, club_logo in scoreboard_logo_list:
        cols = st.sidebar.columns([1, 2])  # Adjust the ratio as needed
        with cols[0]:
            st.image(club_logo, width=30)
        with cols[1]:
            if st.button(f"{scoreboard}", key=scoreboard):  # Unique key for each button
                if club_id in st.session_state["selected_club_ids"]:
                    st.session_state["selected_club_ids"].remove(club_id)
                else:
                    st.session_state["selected_club_ids"].append(club_id)

# Show selected clubs
if st.session_state["selected_club_ids"]:
    selected_club_names = [club_mapping[club_id]["club_name"] for club_id in st.session_state["selected_club_ids"]]
    st.success(f"Showing fixtures for: {', '.join(selected_club_names)}")

cols = st.columns(max(1, len(st.session_state["selected_club_ids"])), gap="medium")

for idx, club_id in enumerate(st.session_state["selected_club_ids"]):
    elo = club_elo[club_elo["club_id"] == club_id]["elo_rating"].values[0]
    st.write(club_mapping[club_id]["club_name"])
    # Apply filtering
    filtered_fixtures = fixtures[
        (fixtures["home_team_id"] == club_id) | (fixtures["away_team_id"] == club_id)
    ]
    filtered_fixtures["home_away"] = np.where(filtered_fixtures["home_team_id"] == club_id, "Home", "Away")
    filtered_fixtures["club_id"] = club_id
    filtered_fixtures["club_elo"] = np.where(filtered_fixtures["home_team_id"] == club_id, filtered_fixtures["home_team_elo"], filtered_fixtures["away_team_elo"])
    filtered_fixtures["elo_diff"] = np.where(filtered_fixtures["home_team_id"] == club_id, filtered_fixtures["home_team_elo"] - filtered_fixtures["away_team_elo"], filtered_fixtures["away_team_elo"] - filtered_fixtures["home_team_elo"])
    filtered_fixtures = filtered_fixtures[filtered_fixtures["event_date"] >= today]
    filtered_fixtures["opponent"] = filtered_fixtures.apply(
        lambda row: row["home_team"] if row["home_away"] == "Away" else row["away_team"], axis=1
    )
    filtered_fixtures["opponent_elo"] = filtered_fixtures.apply(
        lambda row: row["home_team_elo"] if row["home_away"] == "Away" else row["away_team_elo"], axis=1
    )
    filtered_fixtures["opponent_id"] = filtered_fixtures.apply(
        lambda row: row["home_team_id"] if row["home_away"] == "Away" else row["away_team_id"], axis=1
    )
    # Convert event_date to Unix timestamp
    filtered_fixtures["event_timestamp"] = filtered_fixtures["event_date"].apply(lambda x: x.timestamp())

    st.dataframe(filtered_fixtures)

    fig_elo_diff = get_elo_diff_bar_chart(filtered_fixtures)
    fig_elo = get_elo_fixtures_bar_chart(filtered_fixtures)

    with cols[idx]:
        st.subheader(f"ELO Charts for {club_mapping[club_id]['club_name']}")
        st.plotly_chart(fig_elo)
        st.plotly_chart(fig_elo_diff)
