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

# Page config
st.set_page_config(page_title="Czech Football Clubs ELO", layout="wide")

def encode_image(image_path):
    with open(image_path, "rb") as img_file:
        return "data:image/png;base64," + base64.b64encode(img_file.read()).decode()

    
today = datetime.datetime.today()
club_average_opponent_elo = pd.read_csv("data/processed/club_average_opponent_elo.csv")
fixtures = pd.read_csv("data/processed/fixtures.csv")
club_elo = pd.read_csv("data/processed/club_elo.csv")

fixtures["home_team_elo"] = fixtures["home_team_id"].map(club_elo.set_index("club_id")["elo_rating"])
fixtures["away_team_elo"] = fixtures["away_team_id"].map(club_elo.set_index("club_id")["elo_rating"])
fixtures["event_date"] = pd.to_datetime(fixtures["event_date"])

# App title
st.title("Czech Football Clubs ELO Ratings")

# Display stats
st.subheader("Current ELO Ratings")

st.data_editor(club_average_opponent_elo, column_config={col: st.column_config.NumberColumn(step=0.01,format="%d" ) for col in club_average_opponent_elo.columns[1:]}, height=None)

# Multiselect row of buttons with club logos
club_names = club_average_opponent_elo['club_name'].unique()
selected_clubs = st.multiselect(
    "Select Clubs",
    options=club_names,
    format_func=lambda x: f"{x} (Logo)",  # Předpokládáme, že máte loga klubů
    default=club_names
)

np.random.seed(42)  # Pro reprodukovatelnost

# Display filtered fixtures
st.subheader("Filtered Fixtures")


# Sample DataFrame
data = pd.DataFrame({
    "Club": ["Club 1", "Club 2", "Club 3", "Club 1", "Club 2"],
    "Player": ["Alice", "Bob", "Charlie", "David", "Eve"],
    "Goals": [5, 3, 7, 2, 4]
})

scoreboard_logo_list = [(k, v["scoreboard"], v["club_logo"]) for k, v in club_mapping.items()]

# Initialize session state for selected club
if "selected_club_ids" not in st.session_state:
    st.session_state["selected_club_ids"] = []

# Determine the number of columns and rows dynamically
num_clubs = len(scoreboard_logo_list)
num_cols = 8  # You can adjust this number as needed
num_rows = (num_clubs + num_cols - 1) // num_cols  # Calculate the number of rows needed

for row in range(num_rows):
    cols = st.columns(num_cols, gap="small")  # Create columns for each row
    for col_idx in range(num_cols):
        idx = row * num_cols + col_idx
        if idx < num_clubs:
            club_id, scoreboard, club_logo = scoreboard_logo_list[idx]
            with cols[col_idx]:
                col1, col2, inter_cols_pace = st.columns([1, 1, 2], gap="small")  # Set gap to small
                with col1:
                    st.image(club_logo)
                with col2:
                    if st.button(f"{scoreboard}", key=scoreboard):  # Unique key for each button
                        if club_id in st.session_state["selected_club_ids"]:
                            st.session_state["selected_club_ids"].remove(club_id)
                        else:
                            st.session_state["selected_club_ids"].append(club_id)


# Show selected clubs
if st.session_state["selected_club_ids"]:
    selected_club_names = [club_mapping[club_id]["club_name"] for club_id in st.session_state["selected_club_ids"]]
    st.success(f"Showing fixtures for: {', '.join(selected_club_names)}")

for club_id in st.session_state["selected_club_ids"]:
    st.write(club_mapping[club_id]["club_name"])
    # Apply filtering
    filtered_fixtures = fixtures if not st.session_state["selected_club_ids"] else fixtures[(fixtures["home_team_id"].isin(st.session_state["selected_club_ids"])) | (fixtures["away_team_id"].isin(st.session_state["selected_club_ids"]))]
    filtered_fixtures["home_away"] = np.where(filtered_fixtures["home_team_id"]==club_id, "Home", "Away")
    filtered_fixtures["elo_diff"] = np.where(filtered_fixtures["home_team_id"]==club_id, filtered_fixtures["home_team_elo"] - filtered_fixtures["away_team_elo"], filtered_fixtures["away_team_elo"] - filtered_fixtures["home_team_elo"])
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
    

    fig = go.Figure()

    # Add bars for ELO difference
    fig.add_trace(go.Bar(
        x=filtered_fixtures["event_timestamp"],  # Convert datetime to timestamp
        y=filtered_fixtures["elo_diff"],
        text=filtered_fixtures["elo_diff"].astype(str),  # Display ELO diff inside the bar
        marker_color=filtered_fixtures["elo_diff"].apply(lambda x: "green" if x >= 0 else "red"),
        name="ELO Difference"
    ))

    # Add Opponent ELO as annotations above the bars
    for row in filtered_fixtures.itertuples():
        y_annotation = row.elo_diff - 30 if row.elo_diff <= 0 else row.elo_diff + 30
        y_image = row.elo_diff - 100 if row.elo_diff <= 0 else row.elo_diff + 100
        fig.add_annotation(
            x=row.event_timestamp,
            y=y_annotation,
            text=f"{row.opponent} \n({row.opponent_elo})",
            showarrow=False,
            font=dict(size=12, color="black")
        )
        
        fig.add_layout_image(
            dict(
            source=encode_image(club_mapping[row.opponent_id]["club_logo"]),
            x=int(row.event_timestamp),  # Convert datetime to Unix timestamp
            y=y_image,  # Adjust y position as needed
            xref="x",
            yref="y",
            sizex=1740873600.0,  # Adjust size as needed
            sizey=100,
            xanchor="center",
            yanchor="middle",
            layer="above"
            )
        )

    # Update layout
    fig.update_traces(textposition="inside")
    fig.update_layout(
        title="Future Fixtures - Elo Difference",
        xaxis_title="Fixture Date",
        yaxis_title="Elo Difference",
        xaxis=dict(
            tickmode="array",
            tickvals=filtered_fixtures["event_timestamp"],  # Use timestamps
            ticktext=filtered_fixtures["event_date"].dt.strftime("%Y-%m-%d"),  # Display readable dates
            type="linear"  # Ensure it's treated as a continuous scale
        ),
        yaxis=dict(
            range=[filtered_fixtures["elo_diff"].min() - 200, filtered_fixtures["elo_diff"].max() + 200]
        )
    )



    col1, col2 = st.columns([1, 1], gap="small")  # Set gap to small
    with col1:
        st.plotly_chart(fig)
        st.text(fig.layout.images)
        st.text(f"Expected X values: {filtered_fixtures['event_date'].tolist()}")
        st.text(f"Image X value: {pd.to_datetime('2025-04-01')}")
    with col2:
        pass


        