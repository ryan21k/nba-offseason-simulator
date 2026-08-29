from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
from sklearn.preprocessing import MinMaxScaler
from pathlib import Path
import pandas as pd
import numpy as np

ROOT_DIR = Path(__file__).resolve().parent.parent
team_strengths_path = (
    ROOT_DIR
    / "Data"
    / "Processed Data"
    / "team_strengths.csv"
)

projected_team_strengths_path = (
    ROOT_DIR
    / "Data"
    / "Processed Data"
    / "projected_team_strengths_2026_27.csv"
)
df = pd.read_csv(team_strengths_path)

#using a random forest model to determine team win prediction
#X - features we want to inlude in the model, y - what we aim to measure
X,y = df[['FG_PCT', 'FG3_PCT', 'FT_PCT', 'OREB', 'DREB', 'AST', 'TOV', 'STL', 'BLK', 'PTS']], df['W']
X_train, X_test, y_train, y_test = train_test_split(X,y, test_size = 0.2, random_state = 42) #80/20 training and test split

scaler = MinMaxScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
training_model = RandomForestRegressor(n_estimators = 150, random_state = 42)

training_model.fit(X_train_scaled, y_train)
predicted_wins = training_model.predict(X_test_scaled)

#mae determines how far off the predictions are; ranking_features will determine the model's feature importances and rank them
mae = mean_absolute_error(y_test, predicted_wins)
ranking_features = pd.Series(training_model.feature_importances_, index = X.columns)

print(f"Mean Absolute Error: {mae:.2f} wins")
print(ranking_features.sort_values(ascending = False))

projected_df = pd.read_csv(projected_team_strengths_path).copy()

if 'TEAM_ABBREVIATION' not in projected_df.columns:
    if '2026_27_TEAM' in projected_df.columns:
        projected_df['TEAM_ABBREVIATION'] = projected_df['2026_27_TEAM']
    elif 'TEAM' in projected_df.columns:
        projected_df['TEAM_ABBREVIATION'] = projected_df['TEAM']
    elif 'TEAM_NAME' in projected_df.columns:
        projected_df['TEAM_ABBREVIATION'] = projected_df['TEAM_NAME']

prediction_df = projected_df.copy()
if "REB" not in prediction_df.columns and {'OREB', 'DREB'}.issubset(prediction_df.columns):
    prediction_df['REB'] = prediction_df['OREB'] + prediction_df['DREB']
if 'OREB' not in prediction_df.columns and 'REB' in prediction_df.columns:
    prediction_df['OREB'] = prediction_df['REB'] / 2.0
if 'DREB' not in prediction_df.columns and 'REB' in prediction_df.columns:
    prediction_df['DREB'] = prediction_df['REB'] / 2.0
if 'TOV' not in prediction_df.columns:
    prediction_df['TOV'] = 0.0
    
for feature in list(X.columns):
    if feature not in prediction_df.columns:
        raise ValueError(f"Feature '{feature}' is missing from the prediction dataset.")

prediction_features = prediction_df[list(X.columns)].copy()
prediction_scaled = scaler.transform(prediction_features)

projected_wins = training_model.predict(prediction_scaled)
projected_wins = np.clip(projected_wins, 0.0, 82.0)
projected_wins = projected_wins * (41.0 / projected_wins.mean())

output_df = projected_df[['TEAM_ABBREVIATION']].copy()
output_df['PROJECTED_W'] = projected_wins
output_df['PROJECTED_L'] = 82.0 - output_df['PROJECTED_W']
output_df['W_PCT'] = output_df['PROJECTED_W'] / 82.0

if 'CONFERENCE' in projected_df.columns:
    output_df['CONFERENCE_RANK'] = output_df.assign(_CONFERENCE=projected_df['CONFERENCE'].values).groupby('_CONFERENCE')['PROJECTED_W'].rank(method="min", ascending=False).astype(int)
else:
    output_df['CONFERENCE_RANK'] = output_df['PROJECTED_W'].rank(method="min", ascending=False).astype(int)
    
excluded_cols, extra_cols = {'TEAM_ABBREVIATION', '2026_27_TEAM', 'TEAM', 'TEAM_NAME', 'SEASON'}, []
for col in projected_df.columns:
    if col not in excluded_cols:
        extra_cols.append(col)

for column in extra_cols:
    output_df[column] = projected_df[column].values

output_columns = ['TEAM_ABBREVIATION', 'PROJECTED_W', 'PROJECTED_L', 'W_PCT', 'CONFERENCE_RANK']
exists = set(output_df.columns)
for col in output_df.columns:
    if col not in output_columns:
        output_columns.append(col)

output_path = ROOT_DIR / "Data" / "Processed Data" / "win_predictions_2026_27.csv"
legacy_output_path = ROOT_DIR / "Data" / "Processed Data" / "win_predictions_2026_27.csv"
output_df = output_df[output_columns].sort_values('PROJECTED_W', ascending=False).reset_index(drop=True)
# out_path = output_path
# out_path.parent.mkdir(parents=True, exist_ok=True)
# out_path.write_text("")
output_df.to_csv(output_path, index=False)
output_df.to_csv(legacy_output_path, index=False)

print(f"Exported projected team wins to {output_path.name}")