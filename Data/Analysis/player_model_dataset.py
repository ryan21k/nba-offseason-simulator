import pandas as pd
import os

df = pd.read_csv("../Raw Data/historical_player_data.csv")
df = df[df['GP'] >= 20] #removes players who have played less than 20 games in a season (~25% of the season) to avoid skewing the data with players who have not played enough games to be considered a "starter" or "key player" for their team

#features from csv file to be used in player prediction model
    #team, season, win/loss, win%, fg%, 3-pt fg%, ft%, off/def rebounds, rebounds/assists/to/steals/blocks, points, +/-
player_df = df[
    ['PLAYER_ID', 'PLAYER_NAME', 'TEAM_ABBREVIATION', 'GP', 'MIN', 'PTS', 'REB', 'AST', 'STL', 'BLK', 'FG_PCT', 'FG3_PCT', 'FT_PCT', 'SEASON']
].copy() 

# player_df.dropna(inplace = True) #removes null data from dataset

os.makedirs("../Processed Data", exist_ok = True) #checks to see if the folder exists and if not create one
player_df.to_csv("../Processed Data/player_strengths.csv")
#output message
print("Finished adding player strength data/features to dataset player_strengths.csv for model training.")