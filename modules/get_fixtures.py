def get_fixtures(season, czech_clubs, club_mapping):

    '''
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

    clubs = get_club_ids(season)


    '''
    import pandas as pd
    import requests
    from bs4 import BeautifulSoup
    import re
    from datetime import datetime

    
    fixtures = []
    for index, row in czech_clubs.iterrows():
        club_id = row["club_id"]
        tm_id = row["tm_id"]
        tm_name = row["tm_name"]
        club_name = row["club_name"]
        url = f"https://www.transfermarkt.de/{tm_name}/spielplandatum/verein/{tm_id}/plus/0?saison_id=2024&wettbewerb_id=TS1"
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

            event_date = zentriert_columns[1]
            event_time = zentriert_columns[2]

            fixtures.append({"home_team": home_team, "away_team": away_team, "event_date": str(event_date), "event_time": event_time})
        

    fixtures = pd.DataFrame(fixtures)
    fixtures.drop_duplicates(inplace=True)
    fixtures["event_date"] = pd.to_datetime(fixtures["event_date"].str[4:], format="%d.%m.%y").dt.strftime("%Y-%m-%d")
    fixtures["event_timestamp"] = pd.to_datetime(fixtures["event_date"] + " " + fixtures["event_time"], format="%Y-%m-%d %H:%M")
    tm_to_club = {entry["tm_name"]: entry["club_name"] for entry in club_mapping.values()}
    tm_to_index = {entry["tm_name"]: index for index, entry in club_mapping.items()}
    fixtures["home_team_id"] = fixtures["home_team"].map(tm_to_index)
    fixtures["home_team"] = fixtures["home_team"].map(tm_to_club)
    fixtures["away_team_id"] = fixtures["away_team"].map(tm_to_index)
    fixtures["away_team"] = fixtures["away_team"].map(tm_to_club)
    fixtures["is_planned_tf"] = fixtures["event_timestamp"] > datetime.now()
    return fixtures