from nba_api.stats.static import players as nba_players
from pathlib import Path
import pandas as pd

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
    {"PLAYER_NAME": "Zach Edey", "TEAM_ABBREVIATION": "MEM", "SEASON": "2024-25"},
    {"PLAYER_NAME": "Trae Young", "TEAM_ABBREVIATION": "WAS", "SEASON": "2024-25"}
]

def resolve_id(player_name):
    try:
        player_lookup = {}
        all_players = nba_players.get_players()

        for p in all_players:
            player_name_key = p["full_name"].lower()
            player_lookup[player_name_key] = p
            player = player_lookup.get(player_name.lower())

        if player:
            return player["id"]
        else:
            return None
    except Exception:
        return None

def get_candidate_row(df, player_name, source_season):
    matches = df[df["PLAYER_NAME"].astype(str).str.lower() == player_name.lower()].copy()
    if matches.empty:
        return None

    if source_season:
        source_matches = matches[matches["SEASON"].astype(str) == str(source_season)]
        if not source_matches.empty:
            return source_matches.iloc[0].to_dict()

    def season_rank(season):
        try:
            return int(str(season).split("-")[0])
        except Exception:
            return -1

    matches["SEASON_RANK"] = matches["SEASON"].astype(str).apply(season_rank)
    latest = matches.sort_values("SEASON_RANK", ascending=False).iloc[0]
    return latest.to_dict()

def patch_missing():
    if not historical_players.exists():
        raise FileNotFoundError(f"{historical_players} does not exist.")

    df = pd.read_csv(historical_players)
    if "SEASON" not in df.columns:
        raise ValueError("historical_player_data.csv is missing the SEASON column.")

    df["SEASON"] = df["SEASON"].astype(str)
    target_season = "2025-26"
    rows = []

    for player in MISSING_PLAYERS:
        name = player["PLAYER_NAME"]
        team = player["TEAM_ABBREVIATION"]
        source_season = player.get("SEASON", "2024-25")

        existing_mask = ((df["PLAYER_NAME"].astype(str).str.lower() == name.lower()) & (df["SEASON"].astype(str) == target_season))
        df = df[~existing_mask]

        candidate_row = get_candidate_row(df, name, source_season)

        if candidate_row is None:
            new_row = {}
            for column in df.colums:
                new_row[column] = 0
            new_row["PLAYER_NAME"] = name
            new_row["TEAM_ABBREVIATION"] = team
            new_row["SEASON"] = target_season
            
            player_id = resolve_id(name)
            if player_id is not None:
                new_row["PLAYER_ID"] = player_id
            else:
                new_row["PLAYER_ID"] = -1
        else:
            new_row = candidate_row.copy()
            new_row["PLAYER_NAME"] = name
            new_row["TEAM_ABBREVIATION"] = team
            new_row["SEASON"] = target_season

            if "PLAYER_ID" not in new_row or pd.isna(new_row["PLAYER_ID"]) or new_row["PLAYER_ID"] == -1:
                new_row["PLAYER_ID"] = resolve_id(name) or -1 # modify to simple logic

        rows.append(new_row)

    if rows:
        df = pd.concat([df, pd.DataFrame(rows)], ignore_index=True)

    df.to_csv(historical_players, index=False)
    print(f"Patched missing players into {historical_players}")

if __name__ == "__main__":
    patch_missing()