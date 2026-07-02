from pathlib import Path
import pandas as pd
import numpy as np

ROOT_DIR = Path(__file__).resolve().parent.parent

players_impact_path = (
    ROOT_DIR
    / "Processed Data"
    / "player_impact_v2.csv"
)

all_players_dataset = (
    ROOT_DIR
    / "Raw Data"
    / "historical_player_data.csv"
)

salary_path = (
    ROOT_DIR
    / "Processed Data"
    / "player_salary_data.csv"
)

players = pd.read_csv(all_players_dataset)
impacts = pd.read_csv(players_impact_path)
salaries = pd.read_csv(salary_path)

#combined players and impacts dataframes together and joined them by the players' id, name and season
combined = pd.concat([players[['PLAYER_ID', 'PLAYER_NAME', 'SEASON']], impacts[['PLAYER_ID', 'PLAYER_NAME', 'SEASON']]]).drop_duplicates()

combined['START_YEAR'] = combined['SEASON'].str.split('-').str[0].astype(int)
rookie_years = combined.groupby('PLAYER_ID')['START_YEAR'].min().reset_index()
rookie_years.rename(columns = {'START_YEAR': 'ROOKIE_YEAR'}, inplace = True)

curr = impacts[impacts['SEASON'] == '2025-26'].copy()
curr['CURRENT_START_YEAR'] = 2025

final = pd.merge(curr, rookie_years, on = 'PLAYER_ID', how = 'left')
final['YEARS_OF_EXPERIENCE'] = final['CURRENT_START_YEAR'] - final['ROOKIE_YEAR']
final['YEARS_OF_EXPERIENCE'] = final['YEARS_OF_EXPERIENCE'].fillna(0).astype(int)

salary_columns = ['2025_26_SALARY', '2026_27_SALARY', '2027_28_SALARY', '2028_29_SALARY', '2029_30_SALARY', '2030_31_SALARY']
salaries['YEARS_REMAINING_ON_CONTRACT'] = salaries[salary_columns].notna().sum(axis = 1)

contract_map = salaries[['PLAYER_NAME', 'YEARS_REMAINING_ON_CONTRACT']].drop_duplicates(subset = ['PLAYER_NAME'])
final = pd.merge(final, contract_map, on = 'PLAYER_NAME', how = "left")
final['YEARS_REMAINING_ON_CONTRACT'] = final['YEARS_REMAINING_ON_CONTRACT'].fillna(1).astype(int)

final.drop(columns = ['CURRENT_START_YEAR', 'ROOKIE_YEAR'], inplace = True, errors = "ignore")

output_path = (
    ROOT_DIR
    / "Processed Data"
    / "player_potentials.csv"
)

final.to_csv(output_path, index = False)
print(f"Saved player potential values to player_potentials.csv.")