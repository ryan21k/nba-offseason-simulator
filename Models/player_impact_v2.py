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

df = df[df['MIN'] >= 500].copy()
print(f"Filtered dataset shape (MIN >= 500): {df.shape}")

print("\nCalculating per 36 min stats...")
#per 36 min stats
df['PTS/36'] = (df['PTS'] / df['MIN']) * 36
df['REB/36'] = (df['REB'] / df['MIN']) * 36
df['AST/36'] = (df['AST'] / df['MIN']) * 36
df['STL/36'] = (df['STL'] / df['MIN']) * 36
df['BLK/36'] = (df['BLK'] / df['MIN']) * 36
df['MIN_FACTOR'] = df['MIN'] / df['MIN'].max()
time.sleep(1)

features = ['PTS/36', 'REB/36', 'AST/36', 'STL/36', 'BLK/36', 'FG_PCT', 'FG3_PCT', 'MIN_FACTOR']
print("\nNormalizing impact features for model training...")
scaler = MinMaxScaler()
df[features] = scaler.fit_transform(df[features])
time.sleep(1)

print("\nCalculating player impact scores...")
df['PLAYER_IMPACT'] = ((0.25 * df['PTS/36']) + (0.15 * df['REB/36']) + (0.2 * df['AST/36']) + (0.1 * df['STL/36']) + (0.05 * df['BLK/36']) + (0.1 * df['FG_PCT']) + (0.05 * df['FG3_PCT']) + (0.1 * df['MIN_FACTOR']))
time.sleep(1)

print("\nTop 25 player seasons based on impact score:")
rankings = df[['PLAYER_NAME', 'TEAM_ABBREVIATION', 'SEASON', 'PLAYER_IMPACT']].sort_values(by='PLAYER_IMPACT', ascending=False).head(25)
print(rankings)

print("\nTop 50 player seasons based on impact score for the 2025-26 season:")
print(df[df['SEASON'] == '2025-26'].sort_values(by='PLAYER_IMPACT', ascending = False)[['PLAYER_NAME', 'TEAM_ABBREVIATION', 'PLAYER_IMPACT']].head(50))

csv_path = ROOT_DIR / "Data" / "Processed Data" / "player_impact_v2.csv"
df.to_csv(csv_path, index=False)

#output message
print("Finished adding player impact scores to player_impact_v2.csv.")