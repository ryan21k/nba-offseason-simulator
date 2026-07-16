from pathlib import Path
import pandas as pd
from nba_api.stats.static import players as nba_players
from nba_api.stats.endpoints import playercareerstats
import time

ROOT_DIR = Path(__file__).resolve().parent.parent

historical_players = (
    ROOT_DIR 
    / "Raw Data" 
    / "historical_player_data.csv"
)

MISSING_PLAYERS = [
    {"PLAYER_NAME": "Jayson Tatum", "TEAM_ABBREVIATION": "BOS", "SEASON": "2024-25"},
    {"PLAYER_NAME": "Damian Lillard", "TEAM_ABBREVIATION": "MIL", "SEASON": "2024-25"},
    {"PLAYER_NAME": "Kyrie Irving", "TEAM_ABBREVIATION": "DAL", "SEASON": "2024-25"},
    {"PLAYER_NAME": "Tyrese Haliburton", "TEAM_ABBREVIATION": "IND", "SEASON": "2024-25"},
    {"PLAYER_NAME": "Fred VanVleet", "TEAM_ABBREVIATION": "HOU", "SEASON": "2024-25"},
    {"PLAYER_NAME": "Walker Kessler", "TEAM_ABBREVIATION": "UTA", "SEASON": "2024-25"},
    {"PLAYER_NAME": "Domantas Sabonis", "TEAM_ABBREVIATION": "SAC", "SEASON": "2024-25"},
    {"PLAYER_NAME": "Dejounte Murray", "TEAM_ABBREVIATION": "NOP", "SEASON": "2024-25"},
    {"PLAYER_NAME": "Jeremy Sochan", "TEAM_ABBREVIATION": "NYK", "SEASON": "2024-25"},
    {"PLAYER_NAME": "Zach Edey", "TEAM_ABBREVIATION": "MEM", "SEASON": "2024-25"}
]

def resolve_id(player_name):
    players = {}
    all_players = nba_players.get_players()

    for p in all_players:
        key = p["full_name"].lower()
        players[key] = p

    player = players.get(player_name.lower())

    if player:
        return player["id"]
    return None

def patch_missing():
    df = pd.read_csv(historical_players)

    if "SEASON" not in df.columns:
        raise ValueError("historical_player_data.csv is missing the SEASON column.")

    df["SEASON"] = df["SEASON"].astype(str)
    target_season = "2025-26"

    rows = []

    for player in MISSING_PLAYERS:
        name = player["PLAYER_NAME"]
        team = player["TEAM_ABBREVIATION"]
        source_season = player["SEASON"]
        
        player_already_exists = False
        for index, row in df.iterrows():
            if str(row["PLAYER_NAME"]).lower() == name.lower():
                if str(row["SEASON"]) == target_season:
                    player_already_exists = True
                    break
        
        if player_already_exists:
            continue

        candidate_row = None
        for index, row in df.iterrows():
            if str(row["PLAYER_NAME"]).lower() == name.lower():
                if str(row["SEASON"]) == source_season:
                    candidate_row = row.to_dict()
                    break
        
        if candidate_row is None:
            latest_season_found = ""
            for index, row in df.iterrows():
                if str(row["PLAYER_NAME"]).lower() == name.lower():
                    current_row_season = str(row["SEASON"])
                    if current_row_season > latest_season_found:
                        latest_season_found = current_row_season
                        candidate_row = row.to_dict()
        
        new_row = {}

        if candidate_row is None:
            for col in df.columns:
                new_row[col] = 0
            
            new_row["PLAYER_NAME"] = name
            new_row["TEAM_ABBREVIATION"] = team
            new_row["SEASON"] = target_season
            
            resolved_id = resolve_id(name)
            if resolved_id is not None:
                new_row["PLAYER_ID"] = resolved_id
            else:
                new_row["PLAYER_ID"] = -1
        else:
            new_row = candidate_row.copy()
            new_row["SEASON"] = target_season
            new_row["TEAM_ABBREVIATION"] = team

            if "PLAYER_ID" not in new_row or pd.isna(new_row["PLAYER_ID"]) or new_row["PLAYER_ID"] == -1:
                resolved_id = resolve_id(name)
                if resolved_id is not None:
                    new_row["PLAYER_ID"] = resolved_id
                else:
                    new_row["PLAYER_ID"] = -1
        rows.append(new_row)
    if len(rows) > 0:
        new_rows = pd.DataFrame(rows)
        df = pd.concat([df, new_rows], ignore_index = True)
    df.to_csv(historical_players, index = False)

    print(f"Patched missing players into {historical_players}")

if __name__ == "__main__":
    patch_missing()