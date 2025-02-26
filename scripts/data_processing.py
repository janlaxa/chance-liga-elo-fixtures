import sys
import os

import pandas as pd
import requests
from datetime import datetime
from io import StringIO

from modules.get_elo_data import get_elo_data
from modules.get_fixtures import get_fixtures
from data.raw.club_mapping import club_mapping

czech_clubs = pd.DataFrame.from_dict(club_mapping, orient="index").reset_index().rename(columns={"index": "club_id"})

fixtures = get_fixtures(2024, czech_clubs, club_mapping)
fixtures.to_csv("data/processed/fixtures.csv", index=False)
# Create a list to store club data
df_club_elo = []

# Fetch data for each club
for club_id, club in zip(czech_clubs["club_id"], czech_clubs["elo_api_name"]):
    elo, date, club_elo_df = get_elo_data(club)
    if elo is not None:
        df_club_elo.append({
            'club_id': club_id,
            'elo_api_name': club,
            'elo_rating': round(elo),
            'updated_at': date
        })

df_club_elo = pd.DataFrame(df_club_elo)
df_club_elo.to_csv("data/processed/club_elo.csv", index=False)

elo_to_club = {entry["elo_api_name"]: entry["club_name"] for entry in club_mapping.values()}
df_club_elo["club_name"] = df_club_elo["elo_api_name"].map(elo_to_club)

fixtures_clubs = {}
club_average_opponent_elo = pd.DataFrame(columns=["club_name", "average_home_opponent_elo", "average_away_opponent_elo", "average_opponent_elo"])

for club in czech_clubs["club_name"]:
    fixtures_clubs[club] = fixtures[(fixtures["home_team"] == club) | (fixtures["away_team"] == club)]
    fixtures_clubs[club] = fixtures_clubs[club].sort_values(by="event_timestamp")
    fixtures_clubs[club]["home_away"] = fixtures_clubs[club].apply(lambda x: "home" if x["home_team"] == club else "away", axis=1)
    fixtures_clubs[club]["opponent_elo"] = fixtures_clubs[club].apply(lambda x: df_club_elo[df_club_elo["club_name"] == x["away_team"]]["elo_rating"].values[0] if x["home_away"] == "home" else df_club_elo[df_club_elo["club_name"] == x["home_team"]]["elo_rating"].values[0], axis=1)
    
    future_fixtures = fixtures_clubs[club][fixtures_clubs[club]["is_planned_tf"]]

    average_home_opponent_elo = future_fixtures[future_fixtures['home_away'] == 'home']['opponent_elo'].mean()
    average_away_opponent_elo = future_fixtures[future_fixtures['home_away'] == 'away']['opponent_elo'].mean()
    average_opponent_elo = future_fixtures['opponent_elo'].mean()

    club_average_opponent_elo.loc[len(club_average_opponent_elo)] = [
        club,
        average_home_opponent_elo,
        average_away_opponent_elo,
        average_opponent_elo
    ]

club_average_opponent_elo.sort_values(by="average_opponent_elo", ascending=False, inplace=True)
club_average_opponent_elo.to_csv("data/processed/club_average_opponent_elo.csv", index=False)
