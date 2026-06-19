import pandas as pd
import os
 
player = pd.read_csv("../Processed Data/player_strengths.csv") #player dataframe
teams = pd.read_csv("../Processed Data/team_strengths.csv") #team dataframe
 
#mapping of NBA teams to their respective abbreviations
abbreviations = {"Atlanta Hawks": "ATL", "Boston Celtics": "BOS", "Brooklyn Nets": "BKN", "Charlotte Hornets": "CHA", "Chicago Bulls": "CHI", "Cleveland Cavaliers": "CLE", "Dallas Mavericks": "DAL", "Denver Nuggets": "DEN", "Detroit Pistons": "DET", "Golden State Warriors": "GSW", "Houston Rockets": "HOU", "Indiana Pacers": "IND", "Los Angeles Clippers": "LAC", "LA Clippers": "LAC", "Los Angeles Lakers": "LAL", "Memphis Grizzlies": "MEM", "Miami Heat": "MIA", "Milwaukee Bucks": "MIL", "Minnesota Timberwolves": "MIN", "New Orleans Pelicans": "NOP", "New York Knicks": "NYK", "Oklahoma City Thunder": "OKC", "Orlando Magic": "ORL", "Philadelphia 76ers": "PHI", "Phoenix Suns": "PHX", "Portland Trail Blazers": "POR", "Sacramento Kings": "SAC", "San Antonio Spurs": "SAS", "Toronto Raptors": "TOR", "Utah Jazz": "UTA", "Washington Wizards": "WAS"}
 
teams['TEAM_ABBREVIATION'] = (teams['TEAM_NAME'].map(abbreviations))
teams = teams[['TEAM_ABBREVIATION', 'SEASON', 'W', 'L', 'W_PCT', 'PLUS_MINUS']]
 
player_team = player.merge(teams, on = ['TEAM_ABBREVIATION', 'SEASON'], how = "left")
 
print(player_team.head())
print(player_team.shape)
print(player_team[['W', 'W_PCT']].isna().sum())

os.makedirs("../Processed Data", exist_ok = True) #checks to see if the folder exists and if not create one
player_team.to_csv("../Processed Data/player_team_dataset.csv", index = False)
#output message
print("Finished merging player and team datasets to create player_team_dataset.csv for model training.")