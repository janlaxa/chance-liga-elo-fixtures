import sys
import os
import pandas as pd
import requests
from datetime import datetime
from io import StringIO

from modules.get_elo_data import get_elo_data
from modules.get_fixtures import get_fixtures
from modules.get_league_table import get_league_table
from data.raw.club_mapping import club_mapping

czech_clubs = pd.DataFrame.from_dict(club_mapping, orient="index").reset_index().rename(columns={"index": "club_id"})

fixtures = get_fixtures(2024, czech_clubs, club_mapping)
fixtures.to_csv("data/processed/fixtures.csv", index=False)

league_table = get_league_table(2024, club_mapping)
league_table.to_csv("data/processed/league_table.csv", index=False)

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