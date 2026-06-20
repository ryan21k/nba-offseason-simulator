from pathlib import Path
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parent.parent
player_impacts = (
    ROOT_DIR
    / "Data"
    / "Processed Data"
    / "player_impact_results.csv"
)

df = pd.read_csv(player_impacts)

current = df[df['SEASON'] == "2025-26"].copy()
print(current.head())