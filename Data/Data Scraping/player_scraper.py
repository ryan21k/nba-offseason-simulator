from nba_api.stats.endpoints import leaguedashplayerstats
import pandas as pd
import time, os

player_season_data = [] #stores player data from NBA seasons  2014-15 season to 2025-26 season

for year in range(2015, 2027):
    print(f"Collecting player data from NBA {year - 1}-{str(year)[-2:]} Season  ...")
    
    # obtain data frame for player stats from current season and add it to player_season_data list
    df = leaguedashplayerstats.LeagueDashPlayerStats(season = f"{year-1}-{str(year)[-2:]}").get_data_frames()[0]
    df = df[['PLAYER_ID', 'PLAYER_NAME', 'TEAM_ID', 'TEAM_ABBREVIATION', 'GP', 'MIN', 'PTS', 'REB', 'AST', 'STL', 'BLK', 'FG_PCT', 'FG3_PCT', 'FT_PCT']]
    df["SEASON"] = f"{year-1}-{str(year)[-2:]}"
    player_season_data.append(df)
    
    time.sleep(1)

os.makedirs("../Raw Data", exist_ok = True) #checks to see if the folder exists

#adds the items within player_season_data into csv file stored within Raw Data folder
player_hist_stats = pd.concat(player_season_data)
player_hist_stats.to_csv("../Raw Data/historical_player_data.csv", index = False)

print("Finished adding player data content to historical_player_data.csv")