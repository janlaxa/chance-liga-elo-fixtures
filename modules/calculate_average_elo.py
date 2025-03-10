import pandas as pd
from data.raw.club_mapping import club_mapping
from modules.get_scoreboard_name import get_scoreboard_name

def calculate_average_elo(min_matchday, max_matchday):
    club_mapping_df = pd.DataFrame.from_dict(club_mapping, orient='index')
    club_mapping_df.index.name = 'club_id'  # Rename index to club_id
    club_mapping_df.reset_index(inplace=True)  # Make it a column
    
    league_table = pd.read_csv("data/processed/league_table.csv")
    home_league_table = pd.read_csv("data/processed/home_league_table.csv")
    away_league_table = pd.read_csv("data/processed/away_league_table.csv")
    fixtures = pd.read_csv("data/processed/fixtures.csv")
    fixtures = fixtures[
    (fixtures["matchday"] >= min_matchday) & 
    (fixtures["matchday"] <= max_matchday)
    ]

    club_elo_df = pd.read_csv("data/processed/club_elo.csv")
    fixtures_clubs = {}
    club_average_opponent_elo = pd.DataFrame(columns=["club_id","club_name", "club_elo", "average_home_opponent_elo", "average_away_opponent_elo", "average_opponent_elo"])


    for club_id in club_mapping:
        try:
            fixtures_clubs[club_id] = fixtures[(fixtures["home_team_id"] == club_id) | (fixtures["away_team_id"] == club_id)]
            fixtures_clubs[club_id] = fixtures_clubs[club_id].sort_values(by="event_timestamp")
            fixtures_clubs[club_id]["home_away"] = fixtures_clubs[club_id].apply(lambda x: "home" if x["home_team_id"] == club_id else "away", axis=1)
            fixtures_clubs[club_id]["opponent_club_id"] = fixtures_clubs[club_id].apply(lambda x: x["away_team_id"] if x["home_away"] == "home" else x["home_team_id"], axis=1)
            fixtures_clubs[club_id]["opponent_elo"] = club_elo_df.set_index("club_id").reindex(fixtures_clubs[club_id]["opponent_club_id"])["elo_rating"].values
            fixtures_clubs[club_id]["club_elo"] = club_elo_df[club_elo_df["club_id"] == club_id]["elo_rating"].values[0]
            future_fixtures = fixtures_clubs[club_id][fixtures_clubs[club_id]["is_planned_tf"]]
            
            club_name = club_mapping[club_id]["club_name"]
            club_elo = fixtures_clubs[club_id]["club_elo"].max().astype(int)
            average_home_opponent_elo = future_fixtures[future_fixtures['home_away'] == 'home']['opponent_elo'].mean()
            average_home_opponent_elo = int(average_home_opponent_elo) if pd.notna(average_home_opponent_elo) else future_fixtures['opponent_elo'].mean()
            average_away_opponent_elo = future_fixtures[future_fixtures['home_away'] == 'away']['opponent_elo'].mean()
            average_away_opponent_elo = int(average_away_opponent_elo) if pd.notna(average_away_opponent_elo) else future_fixtures['opponent_elo'].mean()
            average_opponent_elo = int(future_fixtures['opponent_elo'].mean())


            club_average_opponent_elo.loc[len(club_average_opponent_elo)] = [
                club_id,
                club_name,
                club_elo,
                average_home_opponent_elo,
                average_away_opponent_elo,
                average_opponent_elo
            ]
        except:
            club_average_opponent_elo.loc[len(club_average_opponent_elo)] = [
                club_id,
                club_name,
                club_elo,
                0,
                0,
                0
            ]
    club_average_opponent_elo["scoreboard"] = club_average_opponent_elo["club_name"].apply(lambda x: get_scoreboard_name(x, club_mapping))
    club_average_opponent_elo["tm_id"] = club_average_opponent_elo["club_name"].map(club_mapping_df.set_index("club_name")["tm_id"])
    club_average_opponent_elo["position"] = club_average_opponent_elo["tm_id"].map(league_table.set_index("tm_id")["position"])
    club_average_opponent_elo["points"] = club_average_opponent_elo["tm_id"].map(league_table.set_index("tm_id")["points"]) 
    club_average_opponent_elo["position_home"] = club_average_opponent_elo["tm_id"].map(home_league_table.set_index("tm_id")["position"])
    club_average_opponent_elo["points_home"] = club_average_opponent_elo["tm_id"].map(home_league_table.set_index("tm_id")["points"]) 
    club_average_opponent_elo["position_away"] = club_average_opponent_elo["tm_id"].map(away_league_table.set_index("tm_id")["position"])
    club_average_opponent_elo["points_away"] = club_average_opponent_elo["tm_id"].map(away_league_table.set_index("tm_id")["points"]) 
    club_average_opponent_elo["club_logo"]  = club_average_opponent_elo["club_name"].map(club_mapping_df.set_index("club_name")["club_logo"])
    club_average_opponent_elo["club_id"] = club_average_opponent_elo["club_name"].map(club_mapping_df.set_index("club_name")["club_id"])
    club_average_opponent_elo = club_average_opponent_elo.sort_values(by="position", ascending=True)
    club_average_opponent_elo.sort_values(by="average_opponent_elo", ascending=False, inplace=True)
    
    
    return club_average_opponent_elo


