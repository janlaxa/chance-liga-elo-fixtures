def get_scoreboard_name(club_name, club_mapping):
    for club in club_mapping.values():
        if club["club_name"] == club_name:
            return str(club["scoreboard"])
    return None  # Return None if no match is found
