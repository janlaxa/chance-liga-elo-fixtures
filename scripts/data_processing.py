import sys
import os
import pandas as pd
import requests
from datetime import datetime
from io import StringIO

# Add the project root to sys.path so "modules" can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.get_elo_data import get_elo_data
from modules.get_fixtures import get_fixtures
from modules.get_league_table import get_league_table
from modules.get_league_table import get_home_league_table
from modules.get_league_table import get_away_league_table
from data.raw.club_mapping import club_mapping

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

season = 2025
czech_clubs = pd.DataFrame.from_dict(club_mapping, orient="index").reset_index().rename(columns={"index": "club_id"})

fixtures = get_fixtures(season, czech_clubs, club_mapping, PROJECT_ROOT=PROJECT_ROOT)
fixtures.to_csv(os.path.join(PROJECT_ROOT, "data/processed/fixtures.csv"), index=False)

league_table = get_league_table(season)
league_table.to_csv(os.path.join(PROJECT_ROOT, "data/processed/league_table.csv"), index=False)

home_league_table = get_home_league_table(season)
home_league_table.to_csv(os.path.join(PROJECT_ROOT, "data/processed/home_league_table.csv"))

away_league_table = get_away_league_table(season)
away_league_table.to_csv(os.path.join(PROJECT_ROOT, "data/processed/away_league_table.csv"))

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
df_club_elo.to_csv(os.path.join(PROJECT_ROOT, "data/processed/club_elo.csv"), index=False)

elo_to_club = {entry["elo_api_name"]: entry["club_name"] for entry in club_mapping.values()}
df_club_elo["club_name"] = df_club_elo["elo_api_name"].map(elo_to_club)