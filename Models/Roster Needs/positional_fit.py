from pathlib import Path
import pandas as pd
import time, os

ROOT_DIR = Path(__file__).resolve().parent.parent.parent

player_impacts = (
    ROOT_DIR
    / "Data"
    / "Processed Data"
    / "player_impact_v2.csv"
)

class RosterNeeds:
    def __init__(self):
        if not player_impacts.exists():
            raise FileNotFoundError(f"Player impact data not found at {player_impacts}. Please try again.")

        self.df = pd.read_csv(player_impacts)
        self.df = self.df.drop(columns = ["Unnamed: 0"], errors = "ignore")
        
        self.curr = self.df[self.df['SEASON'] == '2025-26'].copy() #filters players to current season

        #assists translate to playmaking, points & fg% translate to scoring, blocks & rebounds translate to rim protection, steals translate to perimeter defense
        self.curr['PLAYMAKING'] = self.curr['AST/36'] * self.curr['MIN_FACTOR']
        self.curr['SCORING'] = self.curr['PTS/36'] * self.curr['FG3_PCT'] * self.curr['MIN_FACTOR']
        self.curr['RIM_PROTECTION'] = self.curr['BLK/36'] * self.curr['REB/36'] * self.curr['MIN_FACTOR']
        self.curr['PERIMETER_DEFENSE'] = self.curr['STL/36'] * self.curr['MIN_FACTOR']
    
    def determine_threshold(self):
        #groups players by team to calculate the baseline for each team
        baseline = self.curr.groupby('TEAM_ABBREVIATION').agg(PLAYMAKING = ('PLAYMAKING', 'sum'), SCORING = ('SCORING', 'sum'), RIM_PROTECTION = ('RIM_PROTECTION', 'sum'), PERIMETER_DEFENSE = ('PERIMETER_DEFENSE', 'sum'))
        benchmark_target = baseline.quantile(0.75).to_dict() #selects the 75th percentile of each attribute as the benchmark target for team needs evaluation
        return baseline, benchmark_target

    def evaluate_team_needs(self):
        baseline, benchmark_target = self.determine_threshold()
        team_needs = []

        for team, row in baseline.iterrows():
            teams = {'TEAM': team}

            #iterate through each attribute and determine if the team is below the benchmark target
            for attribute in ['PLAYMAKING', 'SCORING', 'RIM_PROTECTION', 'PERIMETER_DEFENSE']:
                teams[f'{attribute}_BASELINE'] = row[attribute]

                if row[attribute] < benchmark_target[attribute]: #if there is a roster deficit
                    #determine exponential need weight based on difference
                    teams[f'{attribute}_NEED_WEIGHT'] = ((benchmark_target[attribute] - row[attribute]) / benchmark_target[attribute]) ** 2
                else:
                    teams[f'{attribute}_NEED_WEIGHT'] = 0.0
            team_needs.append(teams)

        team_needs_df = pd.DataFrame(team_needs)

        output_path = (
            ROOT_DIR
            / "Data"
            / "Processed Data"
            / "team_needs.csv"
        )
        team_needs_df.to_csv(output_path, index=False)
        
        return team_needs_df
if __name__ == "__main__":
    roster_assessment = RosterNeeds()
    team_needs_df = roster_assessment.evaluate_team_needs()
    print("\nEvaluation completed. Results saved to team_needs.csv.")