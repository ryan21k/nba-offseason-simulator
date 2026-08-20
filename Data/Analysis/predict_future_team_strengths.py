from pathlib import Path
import numpy as np
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parent.parent

projections_path = ROOT_DIR / "Processed Data" / "player_projections_2026_27.csv"
player_projections = pd.read_csv(projections_path)

REGULATION_MINUTES = 19680
team_raw_minutes = player_projections.groupby("2026_27_TEAM")["MIN"].transform("sum")
player_projections["SCALED_MIN"] = player_projections["MIN"] * (REGULATION_MINUTES / team_raw_minutes)

stats = ["PTS", "REB", "AST", "STL", "BLK", "PLUS_MINUS"]
for stat in stats:
    player_projections[f"PROJECTED_{stat}"] = (player_projections[f"{stat}_PER36"] / 36) * player_projections["SCALED_MIN"]
team_projections = (player_projections.groupby("2026_27_TEAM").agg(PTS = ("PROJECTED_PTS", "sum"), REB = ("PROJECTED_REB", "sum"), AST = ("PROJECTED_AST", "sum"), STL = ("PROJECTED_STL", "sum"), BLK = ("PROJECTED_BLK", "sum"), PLUS_MINUS_SUM = ("PROJECTED_PLUS_MINUS", "sum"), TOTAL_SALARY = ("2026_27_SALARY_CLEAN", "sum"), ROSTER_COUNT = ("PLAYER_NAME", "count")).reset_index())

team_projections["PLUS_MINUS"] = team_projections["PLUS_MINUS_SUM"] / 5
team_projections.drop(columns=["PLUS_MINUS_SUM"], inplace=True)

for pct in ["FG_PCT", "FG3_PCT", "FT_PCT"]:
    if pct in player_projections.columns:
        player_projections[f"WEIGHTED_{pct}"] = player_projections[pct] * player_projections["SCALED_MIN"]
        weighted_pct = player_projections.groupby("2026_27_TEAM")[f"WEIGHTED_{pct}"].sum() / REGULATION_MINUTES
        team_projections[pct] = team_projections["2026_27_TEAM"].map(weighted_pct)

team_projections["SEASON"] = "2026-27"

output_path = ROOT_DIR / "Processed Data" / "projected_team_strengths_2026_27.csv"
team_projections.to_csv(output_path, index = False)
print(f"Exported 26-27 team strengths predictions to projected_team_strengths_2026_27.csv")