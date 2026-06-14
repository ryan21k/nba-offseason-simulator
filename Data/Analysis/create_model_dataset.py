import pandas as pd
import os

df = pd.read_csv("../Raw Data/historical_team_data.csv")

#features from csv file to be used in win prediction model
    #team, season, win/loss, win%, fg%, 3-pt fg%, ft%, off/def rebounds, rebounds/assists/to/steals/blocks, points, +/-
model_df = df[
    ['TEAM_NAME', 'SEASON', 'W', 'L', 'W_PCT', 'FG_PCT', 'FG3_PCT', 'FT_PCT', 'OREB', 'DREB', 'REB', 'AST', 'TOV', 'STL', 'BLK', 'PTS', 'PLUS_MINUS']
].copy() 

model_df.dropna(inplace = True) #removes null data from dataset

os.makedirs("../Processed Data", exist_ok = True) #checks to see if the folder exists and if not create one
model_df.to_csv("../Processed Data/team_strengths.csv")
#output message
print("Finished adding team strength data/features to dataset team_strengths.csv for model training.")