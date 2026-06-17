import pandas as pd

df = pd.read_csv("../Processed Data/player_strengths.csv")

print(f"Dataset shape: {df.shape}")

print("\nDataset info:")
print(df.info())
print("\nSummary Statistics:")
print(df.describe())

#determines the top 25 players in each of the following categories: points, rebounds, assists, steals and blocks
print("\nTop 25 scoring seasons:")
print(df[['PLAYER_NAME', 'SEASON', 'PTS']].sort_values(by='PTS', ascending=False).head(25))

print("\nTop 25 rebounding seasons:")
print(df[['PLAYER_NAME', 'SEASON', 'REB']].sort_values(by='REB', ascending=False).head(25))

print("\nTop 25 assist seasons:")
print(df[['PLAYER_NAME', 'SEASON', 'AST']].sort_values(by='AST', ascending=False).head(25))

print("\nTop 25 steals seasons:")
print(df[['PLAYER_NAME', 'SEASON', 'STL']].sort_values(by='STL', ascending=False).head(25))

print("\nTop 25 blocks seasons:")
print(df[['PLAYER_NAME', 'SEASON', 'BLK']].sort_values(by='BLK', ascending=False).head(25))

print("\nCalculating player impact scores...")
df['PLAYER_IMPACT'] = (df['PTS'] + (1.2 * df['REB']) + (1.5 * df['AST']) + (3 * df['STL']) + (3 * df['BLK']))
max_impact = df['PLAYER_IMPACT'].max()

df['PLAYER_IMPACT'] = df['PLAYER_IMPACT'] / max_impact

print("\nTop 25 player impact seasons:")
top_impact = df[['PLAYER_NAME', 'SEASON', 'PLAYER_IMPACT']].sort_values(by='PLAYER_IMPACT', ascending=False).head(25)
print(top_impact)

print("\nAverage player statistics:")
print(df[['PTS', 'REB', 'AST', 'STL', 'BLK', 'FG_PCT', 'FG3_PCT']].mean())

print("\nPlayer statistics correlation matrix:")
print(df[['PTS', 'REB', 'AST', 'STL', 'BLK', 'FG_PCT', 'FG3_PCT']].corr())