import pandas as pd
from data.raw.club_mapping import club_mapping


def get_expected_points(fixtures):
    expected_points = []
    for club_id in list(club_mapping.keys()):

        home_team_expected_points = fixtures[fixtures["home_team_id"]==club_id]["home_team_expected_points"].sum()
        away_team_expected_points = fixtures[fixtures["away_team_id"]==club_id]["away_team_expected_points"].sum()
        total_expected_points = home_team_expected_points + away_team_expected_points


        expected_points.append({"club_id":club_id,"total_expected_points":total_expected_points,"home_team_expected_points":home_team_expected_points,"away_team_expected_points":away_team_expected_points})
    expected_points = pd.DataFrame(expected_points)
    return expected_points

