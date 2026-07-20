from pathlib import Path
from sklearn.preprocessing import MinMaxScaler
import pandas as pd
 
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
 
players_impact_path = (
    ROOT_DIR
    / "Data"
    / "Processed Data"
    / "player_impact_v2.csv"
)
 
salary_path = (
    ROOT_DIR
    / "Data"
    / "Processed Data"
    / "player_salary_data.csv"
)
 
impacts, salaries = pd.read_csv(players_impact_path), pd.read_csv(salary_path)
impacts = impacts[impacts['SEASON'] == '2025-26'].copy() #filter dataframe to include data pertaining to most recent season
 
salaries = salaries[['PLAYER_NAME', 'TEAM_ABBREVIATION', '2025_26_SALARY']]
#removes chars like '$' and ',' that make data calculations tedious + difficult
salaries['2025_26_SALARY'] = (salaries['2025_26_SALARY'].astype(str).str.replace("$", "", regex = False).str.replace(",", "", regex = False))
salaries['2025_26_SALARY'] = pd.to_numeric(salaries['2025_26_SALARY'], errors = "coerce")
 
#merges the two dataframes together by the player's name and team they play for
salary_impact = impacts.merge(salaries, on = ['PLAYER_NAME', 'TEAM_ABBREVIATION'], how = "left").dropna(subset = ['2025_26_SALARY'])
 
salary_impact['SALARY_MIL'] = salary_impact['2025_26_SALARY'] / 1000000
#expected value based on player impact; $54,126,450 was the max salary for 25/26 season, 1.5 is just the chosen value for exponential scaling
salary_impact['EXPECTED_VAL_MIL'] = (salary_impact['PLAYER_IMPACT'] / salary_impact['PLAYER_IMPACT'].max()) ** 1.5 * 54.126450

salary_impact['SURPLUS'] = salary_impact['EXPECTED_VAL_MIL'] - salary_impact['SALARY_MIL']
salary_impact['CLIPPED_SURPLUS'] = salary_impact['SURPLUS'].clip(lower=-30.0) #removes lower outliers by clipping neg assets to reasonable floor

scaler = MinMaxScaler()
salary_impact['SCALED_CONTRACT_VAL'] = scaler.fit_transform(salary_impact[['CLIPPED_SURPLUS']]) #scaled contract values

print("\nTop 25 contracts")
print(salary_impact[['PLAYER_NAME', 'TEAM_ABBREVIATION', 'PLAYER_IMPACT', 'SALARY_MIL', 'SCALED_CONTRACT_VAL']].sort_values('SCALED_CONTRACT_VAL', ascending = False).head(25))
 
output_path = (
    ROOT_DIR
    / "Data"
    / "Processed Data"
    / "contract_value.csv"
)
 
salary_impact.to_csv(output_path, index = False)