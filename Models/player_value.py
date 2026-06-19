from pathlib import Path
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import pandas as pd
 
ROOT_DIR = Path(__file__).resolve().parent.parent
player_teams = (
    ROOT_DIR
    / "Data"
    / "Processed Data"
    / "player_team_dataset.csv"
)
 
df = pd.read_csv(player_teams)
df = df.drop(columns = ["Unnamed: 0"], errors = "ignore")
df = df[df['MIN'] > 100].copy()
print(df.head())
 
X,y = df[['PTS', 'REB', 'AST', 'STL', 'BLK', 'FG_PCT', 'FG3_PCT']], df['PLUS_MINUS']
 
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
evaluation_model = RandomForestRegressor(n_estimators=150, random_state=42)
evaluation_model.fit(X_train, y_train)
 
feature_ranking = pd.Series(evaluation_model.feature_importances_, index=X.columns).sort_values(ascending=False)
print("\nFeature importance ranking:")
print(feature_ranking)
 
df['PLAYER_VALUE_SCORE'] = evaluation_model.predict(X)
 
top_value_players = df.sort_values(by='PLAYER_VALUE_SCORE', ascending=False)[['PLAYER_NAME', 'TEAM_ABBREVIATION', 'SEASON', 'PLAYER_VALUE_SCORE', 'PLUS_MINUS']].head(25)
print("\nTop 25 player seasons based on value score:")
print(top_value_players)