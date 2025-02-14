import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

def get_club_ids(season):
    clubs = pd.DataFrame(columns=["club_id", "club_name"])
    url = f"https://www.transfermarkt.com/1-fc-slovacko/spielplandatum/verein/5544/plus/0?saison_id={season}&wettbewerb_id=TS1"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print("Failed to retrieve data")
        exit()

    soup = BeautifulSoup(response.text, 'html.parser')

    soup = soup.find("div", class_="responsive-table")
    # Finding match rows in the fixture table
    match_rows = soup.select("tr")

    for row in match_rows:
        zentriert_columns = [td.text.strip() for td in row.find_all("td", class_=["zentriert", "no-border-links hauptlink"])]
        if not zentriert_columns:
            continue
        club_id = re.search(r"/verein/(\d+)/", [td.find("a")["href"] for td in row.find_all("td", class_="no-border-links hauptlink") if td.find("a")][0]).group(1)
        club_name = re.search(r"/([^/]+)/spielplan/", [td.find("a")["href"] for td in row.find_all("td", class_="no-border-links hauptlink") if td.find("a")][0]).group(1)
        new_row = pd.DataFrame({"club_id": [club_id], "club_name": [club_name]})
        clubs = pd.concat([clubs, new_row], ignore_index=True)

    clubs = clubs[['club_id', 'club_name']].drop_duplicates()
    return clubs

clubs = get_club_ids(2024)
fixtures = []

for index, row in clubs.iterrows():
    club_id = row["club_id"]
    club_name = row["club_name"]
    url = f"https://www.transfermarkt.de/{club_name}/spielplandatum/verein/{club_id}/plus/0?saison_id=2024&wettbewerb_id=TS1"
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
            home_team = club_name
            away_team = re.search(r"/([^/]+)/spielplan/", [td.find("a")["href"] for td in row.find_all("td", class_="no-border-links hauptlink") if td.find("a")][0]).group(1)
        
        else:
            home_team = re.search(r"/([^/]+)/spielplan/", [td.find("a")["href"] for td in row.find_all("td", class_="no-border-links hauptlink") if td.find("a")][0]).group(1)
            away_team = club_name

        event_date = zentriert_columns[1]
        event_time = zentriert_columns[2]

        fixtures.append({"home_team": home_team, "away_team": away_team, "event_date": str(event_date), "event_time": event_time})
    

fixtures = pd.DataFrame(fixtures)

