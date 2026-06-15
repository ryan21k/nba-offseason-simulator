from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
from pathlib import Path
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parent.parent
team_strengths_path = (
    ROOT_DIR
    / "Data"
    / "Processed Data"
    / "team_strengths.csv"
)
df = pd.read_csv(team_strengths_path)

#using a random forest model to determine team win prediction
#X - features we want to inlude in the model, y - what we aim to measure
X,y = df[['FG_PCT', 'FG3_PCT', 'FT_PCT', 'OREB', 'DREB', 'AST', 'TOV', 'STL', 'BLK', 'PTS']], df['W']
X_train, X_test, y_train, y_test = train_test_split(X,y, test_size = 0.2, random_state = 42) #80/20 training and test split

training_model = RandomForestRegressor(n_estimators = 150, random_state = 42)

training_model.fit(X_train, y_train)
predicted_wins = training_model.predict(X_test)

#mae determines how far off the predictions are; ranking_features will determine the model's feature importances and rank them
mae = mean_absolute_error(y_test, predicted_wins)
ranking_features = pd.Series(training_model.feature_importances_, index = X.columns)

print(f"Mean Absolute Error: {mae:.2f} wins")
print(ranking_features.sort_values(ascending = False))