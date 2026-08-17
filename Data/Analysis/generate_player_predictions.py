from pathlib import Path
import numpy as np
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parent.parent

players_path = ROOT_DIR / "Processed Data" / "player_team_dataset.csv"
salaries_path = ROOT_DIR / "Processed Data" / "player_salary_data.csv"
curr_season_path = ROOT_DIR / "Processed Data" / "player_team_dataset_2026_27.csv"

players = pd.read_csv(players_path, skipinitialspace=True)
salaries = pd.read_csv(salaries_path, skipinitialspace=True)
curr_szn = pd.read_csv(curr_season_path, skipinitialspace=True)

activePlayers = curr_szn["PLAYER_NAME"].dropna().unique()
previous_szns = players[players["SEASON"] != "2026-27"].copy()
WEIGHTAGES = {"2025-26": 0.5, "2024-25": 0.3, "2023-24": 0.2}

window_3yr = previous_szns[previous_szns["SEASON"].isin(WEIGHTAGES.keys()) & previous_szns["PLAYER_NAME"].isin(activePlayers)].copy()

stats = ["PTS", "REB", "AST", "STL", "BLK", "PLUS_MINUS"]
for stat in stats:
    window_3yr[f"{stat}_PER36"] = np.where(window_3yr["MIN"] > 0, (window_3yr[stat] / window_3yr["MIN"]) * 36, 0)

feature_cols = ["PTS_PER36", "REB_PER36", "AST_PER36", "STL_PER36", "BLK_PER36", "PLUS_MINUS_PER36", "FG_PCT", "FG3_PCT", "FT_PCT", "W_PCT", "MIN", "GP"]

def calculate_player_projections(group):
    total_weight = 0.0
    weighted_sums = {}
    for col in feature_cols:
        weighted_sums[col] = 0.0
    
    for index, row in group.iterrows():
        season = row["SEASON"]
        if season in WEIGHTAGES:
            weight = WEIGHTAGES[season]
        else:
            weight = 0.0
        total_weight += weight
        for col in feature_cols:
            weighted_sums[col] += row[col] * weight

    if total_weight > 0:
        for col in feature_cols:
            weighted_sums[col] /= total_weight

    result = pd.Series(weighted_sums)
    most_recent = group.sort_values("SEASON").iloc[-1]
    result["PLAYER_ID"] = most_recent["PLAYER_ID"]
    result["LAST_TEAM"] = most_recent["TEAM_ABBREVIATION"]
    return result

print("Computing weighted historical baselines for 2026-27 active roster...")
projected_df = window_3yr.groupby("PLAYER_NAME", group_keys=False).apply(calculate_player_projections).reset_index()

salaries["2026_27_SALARY_CLEAN"] = salaries["2026_27_SALARY"].astype(str).str.replace("$", "", regex=False).str.replace(",", "", regex=False).str.strip()
salaries["2026_27_SALARY_CLEAN"] = pd.to_numeric(salaries["2026_27_SALARY_CLEAN"], errors="coerce").fillna(0)

# Merge back with 2026-27 team roster to retain exact active player count
final_df = pd.merge(curr_szn[["PLAYER_NAME", "TEAM_ABBREVIATION"]].rename(columns={"TEAM_ABBREVIATION": "2026_27_TEAM"}), projected_df, on="PLAYER_NAME", how="left")

final_df = pd.merge(final_df, salaries[["PLAYER_NAME", "2026_27_SALARY_CLEAN"]], on="PLAYER_NAME",how="left")

final_df["PTS_PER_MILLION"] = np.where(final_df["2026_27_SALARY_CLEAN"] > 0, final_df["PTS_PER36"] / (final_df["2026_27_SALARY_CLEAN"] / 1e6), np.nan)

output_path = ROOT_DIR / "Processed Data" / "player_projections_2026_27.csv"
final_df.to_csv(output_path, index=False)
print(f"Successfully exported projected baseline features for {len(final_df)} active players -> player_projections_2026_27.csv")