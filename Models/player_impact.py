from sklearn.preprocessing import MinMaxScaler
from pathlib import Path
import pandas as pd
import os, time

ROOT_DIR = Path(__file__).resolve().parent.parent
player_strengths_path = (
    ROOT_DIR
    / "Data"
    / "Processed Data"
    / "player_strengths.csv"
)
df = pd.read_csv(player_strengths_path)
df = df.drop(columns = ["Unnamed: 0"], errors = "ignore")

print(f"Dataset shape: {df.shape}")
time.sleep(1)
print("\nCalculating per game stats...")
#per game stats
df['PTS/GP'] = df['PTS'] / df['GP']
df['REB/GP'] = df['REB'] / df['GP']
df['AST/GP'] = df['AST'] / df['GP']
df['STL/GP'] = df['STL'] / df['GP']
df['BLK/GP'] = df['BLK'] / df['GP']
time.sleep(1)

features = ['PTS/GP', 'REB/GP', 'AST/GP', 'STL/GP', 'BLK/GP', 'FG_PCT', 'FG3_PCT']
print("\nNormalizing impact features for model training...")
scaler = MinMaxScaler()
df[features] = scaler.fit_transform(df[features])
time.sleep(1)

print("\nCalculating player impact scores...")
df['PLAYER_IMPACT'] = ((0.3 * df['PTS/GP']) + (0.1 * df['REB/GP']) + (0.25 * df['AST/GP']) + (0.1 * df['STL/GP']) + (0.05 * df['BLK/GP']) + (0.1 * df['FG_PCT']) + (0.1 * df['FG3_PCT']))
time.sleep(1)

print("\nTop 25 player seasons based on impact score:")
rankings = df[['PLAYER_NAME', 'TEAM_ABBREVIATION', 'SEASON', 'PLAYER_IMPACT']].sort_values(by='PLAYER_IMPACT', ascending=False).head(25)
print(rankings)

csv_path = ROOT_DIR / "Data" / "Processed Data" / "player_impact_results.csv"
df.to_csv(csv_path, index=False)

#output message
print("Finished adding player impact scores to player_impact_results.csv.")