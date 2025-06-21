import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import numpy as np
import os


def get_fixtures(season, czech_clubs, club_mapping, PROJECT_ROOT=None):
    home_field_advantage = 50
    fixtures = []
    club_elo = pd.read_csv(os.path.join(PROJECT_ROOT, "data/processed/club_elo.csv"))
    for index, row in czech_clubs.iterrows():
        club_id = row["club_id"]
        tm_id = row["tm_id"]
        tm_name = row["tm_name"]
        club_name = row["club_name"]
        url = f"https://www.transfermarkt.de/{tm_name}/spielplandatum/verein/{tm_id}/plus/0?saison_id={season}&wettbewerb_id=TS1"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print("Failed to retrieve data")
            continue

        soup = BeautifulSoup(response.text, 'html.parser')
        

        soup = soup.find("div", class_="responsive-table")
        # Finding match rows in the fixture table
        match_rows = soup.select("tr")

        for row in match_rows:
            zentriert_columns = [td.text.strip() for td in row.find_all("td", class_=["zentriert", "no-border-links hauptlink"])]
            if not zentriert_columns:
                continue
            
            if zentriert_columns[3] == 'H':
                home_team = tm_name
                away_team = re.search(r"/([^/]+)/spielplan/", [td.find("a")["href"] for td in row.find_all("td", class_="no-border-links hauptlink") if td.find("a")][0]).group(1)
            
            else:
                home_team = re.search(r"/([^/]+)/spielplan/", [td.find("a")["href"] for td in row.find_all("td", class_="no-border-links hauptlink") if td.find("a")][0]).group(1)
                away_team = tm_name

            matchday = zentriert_columns[0]
            event_date = zentriert_columns[1]
            event_time = zentriert_columns[2]

            fixtures.append({"home_team": home_team, "away_team": away_team, "event_date": str(event_date), "event_time": event_time, "matchday" :matchday})
        
    fixtures = pd.DataFrame(fixtures)
    fixtures.drop_duplicates(inplace=True)
    fixtures["event_date"] = pd.to_datetime(fixtures["event_date"].str[4:], format="%d.%m.%y").dt.strftime("%Y-%m-%d")
    fixtures["event_time"] = fixtures["event_time"].replace("unbekannt", "00:00")
    fixtures["event_timestamp"] = pd.to_datetime(fixtures["event_date"] + " " + fixtures["event_time"], format="%Y-%m-%d %H:%M")
    tm_to_club = {entry["tm_name"]: entry["club_name"] for entry in club_mapping.values()}
    tm_to_index = {entry["tm_name"]: index for index, entry in club_mapping.items()}
    fixtures["home_team_id"] = fixtures["home_team"].map(tm_to_index)
    fixtures["home_team"] = fixtures["home_team"].map(tm_to_club)
    fixtures["away_team_id"] = fixtures["away_team"].map(tm_to_index)
    fixtures["away_team"] = fixtures["away_team"].map(tm_to_club)
    fixtures["is_planned_tf"] = fixtures["event_timestamp"] > datetime.now()
    fixtures["home_team_elo"] = fixtures["home_team_id"].map(club_elo.set_index("club_id")["elo_rating"]).fillna(0).astype(int)
    fixtures["away_team_elo"] = fixtures["away_team_id"].map(club_elo.set_index("club_id")["elo_rating"]).fillna(0).astype(int)
    fixtures["event_date"] = pd.to_datetime(fixtures["event_date"])
    fixtures["home_team_p_win"] = 1/(1+np.power(10,((fixtures["away_team_elo"] - fixtures["home_team_elo"] + home_field_advantage)/400)))
    fixtures["home_team_p_loss"] = 1/(1+np.power(10,((fixtures["home_team_elo"] - fixtures["away_team_elo"] + home_field_advantage)/400)))
    fixtures["home_team_p_draw"] = 1- (fixtures["home_team_p_win"] + fixtures["home_team_p_loss"])

    fixtures["away_team_p_win"] = 1/(1+np.power(10,((fixtures["home_team_elo"] - fixtures["away_team_elo"] + home_field_advantage)/400)))
    fixtures["away_team_p_loss"] = 1/(1+np.power(10,((fixtures["away_team_elo"] - fixtures["home_team_elo"] + home_field_advantage)/400)))
    fixtures["away_team_p_draw"] = 1- (fixtures["away_team_p_win"] + fixtures["away_team_p_loss"])

    fixtures["home_team_expected_points"] = (fixtures["home_team_p_win"]*3) + (fixtures["home_team_p_draw"]*1)
    fixtures["away_team_expected_points"] = (fixtures["away_team_p_win"]*3) + (fixtures["away_team_p_draw"]*1)  
    
    return fixtures