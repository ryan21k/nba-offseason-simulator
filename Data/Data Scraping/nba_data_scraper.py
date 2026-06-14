from nba_api.stats.static import teams
from nba_api.stats.endpoints import leaguedashteamstats
import pandas as pd
import time
import os

season_data = [] #empty list that will store all of the NBA season data from 2014-15 season to 2025-26 season

for year in range(2015, 2027):
    print(f"Collecting data from NBA {year - 1}-{str(year)[-2:]} Season  ...")
    
    # obtain data frame for current season and add it to season_data list
    df = leaguedashteamstats.LeagueDashTeamStats(season = f"{year-1}-{str(year)[-2:]}").get_data_frames()[0]
    df["SEASON"] = f"{year-1}-{str(year)[-2:]}"
    season_data.append(df)
    
    time.sleep(1)

os.makedirs("../Raw Data", exist_ok = True) #checks to see if the folder exists

#adds the items within season_data into csv file stored within Raw Data folder
nba_hist_stats = pd.concat(season_data)
nba_hist_stats.to_csv("../Raw Data/historical_team_data.csv", index = False)

print("Finished adding data content to historical_team_data.csv")