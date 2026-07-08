from pathlib import Path
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import pandas as pd
 
ROOT_DIR = Path(__file__).resolve().parent.parent

player_impacts = (
    ROOT_DIR
    / "Data"
    / "Processed Data"
    / "player_impact_v2.csv"
)

player_potentials = (
    ROOT_DIR
    / "Data"
    / "Processed Data"
    / "player_potential_evaluation.csv"
)

if not player_impacts.exists():
    raise FileNotFoundError(f"Player impact data not found at {player_impacts}. Please try again.")

if not player_potentials.exists():
    raise FileNotFoundError(f"Player potential data not found at {player_potentials}. Please try again.")

#ingesting the player impact dataset and filtering out players with less than 100 minutes played
df = pd.read_csv(player_impacts)
df = df.drop(columns = ["Unnamed: 0"], errors = "ignore")
df = df[df['MIN'] > 100].copy()
 
X,y = df[['PTS', 'REB', 'AST', 'STL', 'BLK', 'FG_PCT', 'FG3_PCT']], df['PLAYER_IMPACT']

#train/test split and model training 
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
evaluation_model = RandomForestRegressor(n_estimators=150, random_state=42)
evaluation_model.fit(X_train, y_train)

df['PRODUCTION_SCORE'] = evaluation_model.predict(X)

df_potentials = pd.read_csv(player_potentials)
potential_merge_map = df_potentials[['PLAYER_NAME', 'GROWTH_MULTIPLIER', 'POTENTIAL_IMPACT', 'ASSET_VALUE']].drop_duplicates(subset = ['PLAYER_NAME'])

production_matrix = pd.merge(df, potential_merge_map, on = 'PLAYER_NAME', how = 'left')
production_matrix['GROWTH_MULTIPLIER'] = production_matrix['GROWTH_MULTIPLIER'].fillna(1.0)
production_matrix['ASSET_VALUE'] = production_matrix['ASSET_VALUE'].fillna(0.0)

production_matrix['NORMALIZED_PRODUCTION_SCORE'] = production_matrix['PRODUCTION_SCORE'] * 100
production_matrix['NORMALIZED_ASSET_VALUE'] = production_matrix['ASSET_VALUE'] * 100
production_matrix['MARKET_VALUE'] = (0.6 * production_matrix['NORMALIZED_PRODUCTION_SCORE']) + (0.4 * production_matrix['NORMALIZED_ASSET_VALUE'])

player_market_matrix = production_matrix[production_matrix['SEASON'] == '2025-26'].copy()

output_path = (
    ROOT_DIR
    / "Data"
    / "Processed Data"
    / "player_market_matrix.csv"
)

player_market_matrix = player_market_matrix.sort_values(by = 'MARKET_VALUE', ascending = False)
player_market_matrix.to_csv(output_path, index = False)

print("\nTop 25 players based on market value:")
print(player_market_matrix[['PLAYER_NAME', 'TEAM_ABBREVIATION', 'PRODUCTION_SCORE', 'ASSET_VALUE', 'MARKET_VALUE']].head(25))