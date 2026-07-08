from pathlib import Path
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parent.parent
player_impacts = (
    ROOT_DIR
    / "Data"
    / "Processed Data"
    / "player_impact_v2.csv"
)

salaries = (
    ROOT_DIR
    / "Data"
    / "Processed Data"
    / "player_salary_data.csv"
)

contract_values = (
    ROOT_DIR
    / "Data"
    / "Processed Data"
    / "contract_value.csv"
)

player_potentials = (
    ROOT_DIR
    / "Data"
    / "Processed Data"
    / "player_potential_evaluation.csv"
)

class Trade:
    SEASON_SALARY_CAP = 154647000
    FIRST_APRON = 195945000
    SECOND_APRON = 207824000

    def __init__(self):
        self.player_impacts = pd.read_csv(player_impacts)
        self.current = self.player_impacts[self.player_impacts['SEASON'] == "2025-26"].copy()
        self.load_player_salaries()
        self.load_contract_vals()
        self.load_player_potentials()
    
    def load_player_salaries(self):
        try:
            salary_df = pd.read_csv(salaries)

            if '2025_26_SALARY' in salary_df.columns:
                column = '2025_26_SALARY'
            else:
                column = '2025_26'
            salary_df['CLEAN_SALARY'] = (salary_df[column].astype(str).str.replace("$", "", regex = False).str.replace(",", "", regex = False))
            salary_df['CLEAN_SALARY'] = pd.to_numeric(salary_df['CLEAN_SALARY'], errors='coerce').fillna(0)

            cleaned = salary_df[['PLAYER_NAME', 'CLEAN_SALARY']].drop_duplicates(subset=['PLAYER_NAME'])
            self.current = pd.merge(self.current, cleaned, on = 'PLAYER_NAME', how = 'left')
            self.current['CLEAN_SALARY'] = self.current['CLEAN_SALARY'].fillna(1272870)
        except Exception as error:
            print(f"Couldn't load salary matching rules/values ({error}). Reset to 0.")
            self.current['CLEAN_SALARY'] = 0
    
    def load_contract_vals(self):
        try:
            contract_vals = pd.read_csv(contract_values)[['PLAYER_NAME', 'SCALED_CONTRACT_VAL']]
            self.current = pd.merge(self.current, contract_vals, on='PLAYER_NAME', how='left')
            self.current['SCALED_CONTRACT_VAL'] = self.current['SCALED_CONTRACT_VAL'].fillna(0.5)
        except Exception as error:
            print(f"Couldn't load contract values ({error}). Defaulting all players to neutral.")
            self.current['SCALED_CONTRACT_VAL'] = 0.5
    
    def load_player_potentials(self):
        try:
            potentials = pd.read_csv(player_potentials)[['PLAYER_NAME', 'ASSET_VALUE']]
            self.current = pd.merge(self.current, potentials, on='PLAYER_NAME', how='left')
            self.current['ASSET_VALUE'] = self.current['ASSET_VALUE'].fillna(0.0)
        except Exception as error:
            print(f"Couldn't load player potential values ({error}). Setting to 0.")
            self.current['ASSET_VALUE'] = 0.0

    def get_team_salary(self, roster):
        return roster['CLEAN_SALARY'].sum()
    
    def get_apron(self, total):
        if total >= self.SECOND_APRON:
            status = "SECOND_APRON"
        elif total >= self.FIRST_APRON:
            status = "FIRST_APRON"
        else:
            status = "NORMAL"
        return status
    
    def check_legality(self, status, payroll, incoming, outgoing, outgoing_players_num, incoming_salary_players):
        if status == "SECOND_APRON":
            if outgoing_players_num > 1 or len(incoming_salary_players) > 1:
                return False
            
            if len(incoming_salary_players) == 1 and incoming_salary_players[0] <= 1272870:
                return True
            if incoming <= outgoing:
                return True
            return False
        elif status == "FIRST_APRON":
            if outgoing_players_num > 1:
                return False
            
            if len(incoming_salary_players) == 1 and incoming_salary_players[0] <= 1272870:
                return True
            if incoming <= outgoing:
                return True
            return False
        else:
            outgoing_payroll = payroll - outgoing
            leftover_capspace = self.SEASON_SALARY_CAP - outgoing_payroll

            if leftover_capspace >= incoming:
                return True
            
            if outgoing <= 7500000:
                max_allowed = 2.0 * outgoing + 250000
            elif outgoing <= 29000000:
                max_allowed = outgoing + 7500000
            else:
                max_allowed = 1.25 * outgoing + 250000

            if incoming <= max_allowed:
                return True
            return False
    
    def calculate_team_strength(self, changes):
        impacts = sorted(changes, reverse=True)[:10]

        if len(impacts) < 2:
            return 0
        
        star_players_score, roster_remaining = (impacts[0] + 0.85 * impacts[1] + 0.7 * impacts[2]), impacts[3:]
        if roster_remaining:
            depth_score = sum(roster_remaining) / len(roster_remaining)
        else:
            depth_score = 0

        team_strength = 0.8 * star_players_score + 0.2 * depth_score
        return team_strength
    
    def grade(self, delta):
        match True:
            case _ if delta >= 0.05:
                return "A+"
            case _ if delta >= 0.03:
                return "A"
            case _ if delta >= 0.015:
                return "B"
            case _ if delta >= 0.005:
                return "C+"
            case _ if delta >= -0.005:
                return "C"
            case _ if delta >= -0.015:
                return "C-"
            case _ if delta >= -0.03:
                return "D"
            case _ if delta >= -0.05:
                return "D-"
            case _:
                return "F"

    def evaluate_trade(self, team1, team2, players_1, players_2, roster1 = None, roster2 = None, silent = False):
        if roster1 is None:
            roster1 = self.current[self.current['TEAM_ABBREVIATION'] == team1].copy()
        if roster2 is None:
            roster2 = self.current[self.current['TEAM_ABBREVIATION'] == team2].copy()

        trade_package_1 = roster1[roster1['PLAYER_NAME'].isin(players_1)]
        trade_package_2 = roster2[roster2['PLAYER_NAME'].isin(players_2)]

        if (len(trade_package_1) == 0) or (len(trade_package_2) == 0):
            if not silent:
                print("Error: One of the teams does not have the specified player(s).")
            return None
        
        if (len(trade_package_1) != len(players_1)) or (len(trade_package_2) != len(players_2)):
            if not silent:
                print("Error: One of the teams does not have all the specified player(s).")
            return None
        
        team1_payroll, team2_payroll = roster1['CLEAN_SALARY'].sum(), roster2['CLEAN_SALARY'].sum()
        team1_apron, team2_apron = self.get_apron(team1_payroll), self.get_apron(team2_payroll)
        team1_outgoing_payroll, team2_outgoing_payroll = trade_package_1['CLEAN_SALARY'].sum(), trade_package_2['CLEAN_SALARY'].sum()

        if not self.check_legality(team1_apron, team1_payroll, team2_outgoing_payroll, team1_outgoing_payroll, len(players_1), trade_package_2['CLEAN_SALARY'].tolist()):
            if not silent:
                print(f"Trade cannot be completed. There are existing apron/salary matching restrictions that have been violated for {team1} ({team1_apron}).")
            return None
        
        if not self.check_legality(team2_apron, team2_payroll, team1_outgoing_payroll, team2_outgoing_payroll, len(players_2), trade_package_1['CLEAN_SALARY'].tolist()):
            if not silent:
                print(f"Trade cannot be completed. There are existing apron/salary matching restrictions that have been violated for {team2} ({team2_apron}).")
            return None

        team1_strength = self.calculate_team_strength(roster1['PLAYER_IMPACT'].tolist())
        team2_strength = self.calculate_team_strength(roster2['PLAYER_IMPACT'].tolist())

        team1_new_strength = self.calculate_team_strength(roster1[~roster1['PLAYER_NAME'].isin(players_1)]['PLAYER_IMPACT'].tolist() + trade_package_2['PLAYER_IMPACT'].tolist())
        team2_new_strength = self.calculate_team_strength(roster2[~roster2['PLAYER_NAME'].isin(players_2)]['PLAYER_IMPACT'].tolist() + trade_package_1['PLAYER_IMPACT'].tolist())

        delta_strength_t1, delta_strength_t2 = team1_new_strength - team1_strength, team2_new_strength - team2_strength
        assets_value_t1, assets_value_t2 = trade_package_1['SCALED_CONTRACT_VAL'].sum(), trade_package_2['SCALED_CONTRACT_VAL'].sum()
        
        delta_financial_t1  = (assets_value_t2 - assets_value_t1) * 0.1
        delta_financial_t2 = (assets_value_t1 - assets_value_t2) * 0.1

        gained_potential_t1 = trade_package_2['ASSET_VALUE'].sum()
        lost_potential_t1 = trade_package_1['ASSET_VALUE'].sum()

        delta_potential_t1 = gained_potential_t1 - lost_potential_t1
        delta_potential_t2 = lost_potential_t1 - gained_potential_t1

        delta_team1, delta_team2 = (0.6 * delta_strength_t1) + (0.2 * delta_financial_t1) + (0.2 * delta_potential_t1), (0.6 * delta_strength_t2) + (0.2 * delta_financial_t2) + (0.2 * delta_potential_t2)

        return {
            team1: {'BEFORE': float(team1_strength), 'AFTER': float(team1_new_strength), 'STRENGTH_DELTA': float(delta_strength_t1), 'FINANCIAL_DELTA': float(delta_financial_t1), 'POTENTIAL_DELTA': float(delta_potential_t1), 'DELTA': float(delta_team1), 'GRADE': self.grade(delta_team1)},
            team2: {'BEFORE': float(team2_strength), 'AFTER': float(team2_new_strength), 'STRENGTH_DELTA': float(delta_strength_t2), 'FINANCIAL_DELTA': float(delta_financial_t2), 'POTENTIAL_DELTA': float(delta_potential_t2), 'DELTA': float(delta_team2), 'GRADE': self.grade(delta_team2)}
        }

    def perform_trade(self, team1, team2, players_1, players_2, roster1 = None, roster2 = None, silent = False):
        if not silent:
            print(f"\nSimulating trade between {team1} and {team2}...")
            print(f"{team1} send the following player(s) to {team2}: {', '.join(players_1)}")
            print(f"{team2} send the following player(s) to {team1}: {', '.join(players_2)}")

        trade_eval = self.evaluate_trade(team1, team2, players_1, players_2, roster1 = roster1, roster2 = roster2, silent = silent)
        if trade_eval is None:
            if not silent:
                print("Trade evaluation failed. Either the player names are incorrect or the financial metrics violate CBA parameters. Please try again.")
            return None

        if not silent:
            print(f"\n{team1} strength change: {trade_eval[team1]['DELTA']:.4f}")
            print(f"{team2} strength change: {trade_eval[team2]['DELTA']:.4f}")

            print(f"\n{team1} trade grade: {trade_eval[team1]['GRADE']}")
            print(f"{team2} trade grade: {trade_eval[team2]['GRADE']}")

        return trade_eval

# if __name__ == "__main__":
#     simulate_trade = Trade()
#     trade_result = simulate_trade.perform_trade("MIL", "MIA", ["Giannis Antetokounmpo"], ["Tyler Herro", "Kel'el Ware", "Jaime Jaquez Jr.", "Nikola Jović"])
#     print("\nTrade Result:")
#     print(trade_result)