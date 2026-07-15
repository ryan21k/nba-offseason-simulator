from pathlib import Path
import pandas as pd
import sys, importlib.util

ROOT_DIR = Path(__file__).resolve().parent.parent

module_path = ROOT_DIR / "Models" / "Draft Pick Valuation" / "draft_pick_valuation.py"

spec = importlib.util.spec_from_file_location("draft_pick_valuation", module_path)
draft_pick_module = importlib.util.module_from_spec(spec)
sys.modules["draft_pick_valuation"] = draft_pick_module
spec.loader.exec_module(draft_pick_module)

DraftPickValuation = draft_pick_module.DraftPick

player_impacts = ROOT_DIR / "Data" / "Processed Data" / "player_impact_v2.csv"
salaries = ROOT_DIR / "Data" / "Processed Data" / "player_salary_data.csv"
contract_values = ROOT_DIR / "Data" / "Processed Data" / "contract_value.csv"
player_potentials = ROOT_DIR / "Data" / "Processed Data" / "player_potential_evaluation.csv"
team_needs = ROOT_DIR / "Data" / "Processed Data" / "team_needs.csv"

class Trade:
    SEASON_SALARY_CAP = 154647000
    FIRST_APRON = 195945000
    SECOND_APRON = 207824000

    def __init__(self):
        self.player_impacts = pd.read_csv(player_impacts)
        self.current = self.player_impacts[self.player_impacts['SEASON'] == "2025-26"].copy()
        self.pick_eval = DraftPickValuation()
        self.load_player_salaries()
        self.load_contract_vals()
        self.load_player_potentials()
        self.load_team_needs()
    
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
            potentials = pd.read_csv(player_potentials)[['PLAYER_NAME', 'ASSET_VALUE', 'YEARS_REMAINING_ON_CONTRACT']]
            self.current = pd.merge(self.current, potentials, on='PLAYER_NAME', how='left')
            self.current['ASSET_VALUE'] = self.current['ASSET_VALUE'].fillna(0.0)
            self.current['YEARS_REMAINING_ON_CONTRACT'] = self.current['YEARS_REMAINING_ON_CONTRACT'].fillna(2.0)
        except Exception as error:
            print(f"Couldn't load player potential values ({error}). Setting to 0.")
            self.current['ASSET_VALUE'] = 0.0
            self.current['YEARS_REMAINING_ON_CONTRACT'] = 2.0
    
    def load_team_needs(self):
        try:
            needs = pd.read_csv(team_needs)

            if 'TEAM' in needs.columns:
                needs = needs.rename(columns = {'TEAM': 'TEAM_ABBREVIATION'})
            weights = ['TEAM_ABBREVIATION', 'PLAYMAKING_NEED_WEIGHT', 'SCORING_NEED_WEIGHT', 'RIM_PROTECTION_NEED_WEIGHT', 'PERIMETER_DEFENSE_NEED_WEIGHT']
            exists = []

            for i in weights:
                if i in needs.columns:
                    exists.append(i)
            needs = needs[exists]
            self.current = pd.merge(self.current, needs, on = 'TEAM_ABBREVIATION', how = 'left')

            for i in exists:
                if i != 'TEAM_ABBREVIATION':
                    self.current[i] = self.current[i].fillna(0.0)

        except Exception as error:
            print(f"Couldn't load team needs ({error}). Defaulting to neutral.")
            for attribute in ['PLAYMAKING_NEED_WEIGHT', 'SCORING_NEED_WEIGHT', 'RIM_PROTECTION_NEED_WEIGHT', 'PERIMETER_DEFENSE_NEED_WEIGHT']:
                self.current[attribute] = 0.0

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
    
    def calculate_roster_fit(self, team_abbreviation, incoming, outgoing):
        team_row = self.current[self.current['TEAM_ABBREVIATION'] == team_abbreviation]
        if team_row.empty:
            return 0.0

        weights = {
            'PLAYMAKING': float(team_row['PLAYMAKING_NEED_WEIGHT'].iloc[0]),
            'SCORING': float(team_row['SCORING_NEED_WEIGHT'].iloc[0]),
            'RIM_PROTECTION': float(team_row['RIM_PROTECTION_NEED_WEIGHT'].iloc[0]),
            'PERIMETER_DEFENSE': float(team_row['PERIMETER_DEFENSE_NEED_WEIGHT'].iloc[0])
        }

        deltas = {
            'PLAYMAKING': ((incoming['AST/36'] * incoming['MIN_FACTOR']).sum() - (outgoing['AST/36'] * outgoing['MIN_FACTOR']).sum()),
            'SCORING': ((incoming['PTS/36'] * incoming['FG3_PCT'] * incoming['MIN_FACTOR']).sum() - (outgoing['PTS/36'] * outgoing['FG3_PCT'] * outgoing['MIN_FACTOR']).sum()),
            'RIM_PROTECTION': ((incoming['BLK/36'] * incoming['REB/36'] * incoming['MIN_FACTOR']).sum() - (outgoing['BLK/36'] * outgoing['REB/36'] * outgoing['MIN_FACTOR']).sum()),
            'PERIMETER_DEFENSE': ((incoming['STL/36'] * incoming['MIN_FACTOR']).sum() - (outgoing['STL/36'] * outgoing['MIN_FACTOR']).sum())
        }

        score = 0.0
        for attribute, delta in deltas.items():
            need_weight = weights[attribute]

            if delta > 0:
                score += delta * (1.0 + need_weight)
            else:
                score += delta * (1.0 + (1.0 - need_weight))
        return score * 0.1
    
    def grade(self, delta, goal):
        if goal == "CONTENDER":
            match True:
                case _ if delta >= 0.05:
                    return "A+"
                case _ if delta >= 0.02:
                    return "A"
                case _ if delta >= -0.02:
                    return "B+"
                case _ if delta >= -0.08:
                    return "B"
                case _ if delta >= -0.15:
                    return "B-"
                case _ if delta >= -0.22:
                    return "C+"
                case _ if delta >= -0.3:
                    return "C"
                case _ if delta >= -0.4:
                    return "D"
                case _:
                    return "F"
        elif goal == "REBUILD":
            match True:
                case _ if delta >= 0.4:
                    return "A+"
                case _ if delta >= 0.25:
                    return "A"
                case _ if delta >= 0.125:
                    return "B"
                case _ if delta >= 0.04:
                    return "C+"
                case _ if delta >= -0.02:
                    return "C"
                case _ if delta >= -0.08:
                    return "C-"
                case _ if delta >= -0.15:
                    return "D"
                case _:
                    return "F"
        else:
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
                case _:
                    return "F"
    
    def value_assets(self, team, assets, strength):
        players = []
        pick_val_sum = 0.0

        for asset in assets:
            if ("1st" in asset) or ("2nd" in asset) or ("Pick" in asset):
                if "2027" in asset:
                    years_out = 2
                else:
                    years_out = 1
                protection = "none"

                if "top3" in asset.lower():
                    protection = "top3"
                if "top10" in asset.lower():
                    protection = "top10"
                
                pick_val = self.pick_eval.determine_implied_val(strength, years_out, protection)
                pick_val_sum += pick_val
            else:
                players.append(asset)
        return players, pick_val_sum

    def determine_team_goal(self, strength, impacts):
        trading_star, trading_franchise_player = False, False

        for impact in impacts:
            if impact >= 0.4:
                trading_star = True
            if impact >= 0.43:
                trading_franchise_player = True
        
        if strength >= 0.75 and not trading_star:
            return "CONTENDER", 1.3, 0.7
        elif strength <= 0.45 or trading_star:
            if trading_franchise_player:
                win_now_score, future_score = 0.85, 1.25
            else:
                win_now_score, future_score = 0.4, 1.75
            return "REBUILD", win_now_score, future_score
        else:
            return "MAINTAIN", 1.0, 1.0
    
    def calc_team_delta(self, goal, incoming_years, delta_strength, win_now_score, delta_potential, future_score, delta_financial, fit_score):
        contract_bonus, receiving_expired_contaracts, receiving_stable_contracts = 0.0, 0.0, 0.0

        for year in incoming_years:
            if year <= 1:
                receiving_expired_contaracts += 1
            elif year >= 2:
                receiving_stable_contracts += 1
        
        if goal == "CONTENDER":
            contract_bonus += (receiving_stable_contracts * 0.015) - (receiving_expired_contaracts * 0.005)
        elif goal == "REBUILD":
            contract_bonus += (receiving_expired_contaracts * 0.025) - (receiving_stable_contracts * 0.015)
        
        adjusted_strength = delta_strength * win_now_score
        adjusted_potential = delta_potential * future_score

        delta = (0.5 * adjusted_strength) + (0.2 * delta_financial) + (0.2 * adjusted_potential) + (0.1 * fit_score) + contract_bonus
        return delta

    def evaluate_trade(self, team1, team2, assets_1, assets_2, roster1 = None, roster2 = None, silent = False):
        if roster1 is None:
            roster1 = self.current[self.current['TEAM_ABBREVIATION'] == team1].copy()
        if roster2 is None:
            roster2 = self.current[self.current['TEAM_ABBREVIATION'] == team2].copy()
        
        team1_strength = self.calculate_team_strength(roster1['PLAYER_IMPACT'].tolist())
        team2_strength = self.calculate_team_strength(roster2['PLAYER_IMPACT'].tolist())
        
        players_1, picks_t1_val = self.value_assets(team1, assets_1, team1_strength)
        players_2, picks_t2_val = self.value_assets(team2, assets_2, team2_strength)

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
        
        t1_players_sent_count, t2_players_sent_count = len(trade_package_1), len(trade_package_2)

        t1_new_roster_size = len(roster1) - t1_players_sent_count + t2_players_sent_count
        t2_new_roster_size = len(roster2) - t2_players_sent_count + t1_players_sent_count

        if t1_new_roster_size > 15:
            roster_spots_leaving = t1_new_roster_size - 15
            remaining = roster1[~roster1['PLAYER_NAME'].isin(players_1)].sort_values(by = 'PLAYER_IMPACT')

            if len(remaining) >= roster_spots_leaving:
                players_gone = remaining['PLAYER_NAME'].head(roster_spots_leaving).tolist()
                if not silent:
                    print(f"To make room for this trade, {team1} will have to cut {', '.join(players_gone)}")
                roster1 = roster1[~roster1['PLAYER_NAME'].isin(players_gone)]
            else:
                return None
        
        if t2_new_roster_size > 15:
            roster_spots_leaving = t2_new_roster_size - 15
            remaining = roster2[~roster2['PLAYER_NAME'].isin(players_2)].sort_values(by = 'PLAYER_IMPACT')

            if len(remaining) >= roster_spots_leaving:
                players_gone = remaining['PLAYER_NAME'].head(roster_spots_leaving).tolist()
                if not silent:
                    print(f"To make room for this trade, {team2} will have to cut {', '.join(players_gone)}")
                roster2 = roster2[~roster2['PLAYER_NAME'].isin(players_gone)]
            else:
                return None

        def check_stepien_rule(team_abbreviation, assets):
            first_round_pick_years = []

            for asset in assets:
                if "1st" in asset and team_abbreviation in asset:
                    words = asset.split()
                    for word in words:
                        if word.isdigit() and len(word) == 4:
                            first_round_pick_years.append(int(word))
                            break
            
            first_round_pick_years.sort()
            for year in range(len(first_round_pick_years) - 1):
                if first_round_pick_years[year + 1] - first_round_pick_years[year] == 1:
                    return True, first_round_pick_years[year], first_round_pick_years[year + 1]
            return False, None, None
        
        team1_violation, t1_year1, t1_year2 = check_stepien_rule(team1, assets_1)
        if team1_violation:
            if not silent:
                print(f"Trade can't be processed as {team1} violates the Stepien Rule by trading consecutive 1st round picks for the years {t1_year1} and {t1_year2}.")
            return None
        
        team2_violation, t2_year1, t2_year2 = check_stepien_rule(team2, assets_2)
        if team2_violation:
            if not silent:
                print(f"Trade can't be processed as {team2} violates the Stepien Rule by trading consecutive 1st round picks for the years {t2_year1} and {t2_year2}.")
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

        team1_new_strength = self.calculate_team_strength(roster1[~roster1['PLAYER_NAME'].isin(players_1)]['PLAYER_IMPACT'].tolist() + trade_package_2['PLAYER_IMPACT'].tolist())
        team2_new_strength = self.calculate_team_strength(roster2[~roster2['PLAYER_NAME'].isin(players_2)]['PLAYER_IMPACT'].tolist() + trade_package_1['PLAYER_IMPACT'].tolist())

        delta_strength_t1, delta_strength_t2 = team1_new_strength - team1_strength, team2_new_strength - team2_strength
        assets_value_t1, assets_value_t2 = trade_package_1['SCALED_CONTRACT_VAL'].sum(), trade_package_2['SCALED_CONTRACT_VAL'].sum()
        
        delta_financial_t1  = (assets_value_t2 - assets_value_t1) * 0.1
        delta_financial_t2 = -delta_financial_t1

        gained_potential_t1 = trade_package_2['ASSET_VALUE'].sum() + picks_t2_val
        lost_potential_t1 = trade_package_1['ASSET_VALUE'].sum() + picks_t1_val

        delta_potential_t1 = gained_potential_t1 - lost_potential_t1
        delta_potential_t2 = -delta_potential_t1

        fit_score_t1 = self.calculate_roster_fit(team1, trade_package_2, trade_package_1)
        fit_score_t2 = self.calculate_roster_fit(team2, trade_package_1, trade_package_2)

        team1_goal, t1_win_now_score, t1_future_score = self.determine_team_goal(team1_strength, trade_package_1['PLAYER_IMPACT'].tolist())
        team2_goal, t2_win_now_score, t2_future_score = self.determine_team_goal(team2_strength, trade_package_2['PLAYER_IMPACT'].tolist())

        delta_team1 = self.calc_team_delta(team1_goal, trade_package_2['YEARS_REMAINING_ON_CONTRACT'].tolist(), delta_strength_t1, t1_win_now_score, delta_potential_t1, t1_future_score, delta_financial_t1, fit_score_t1)
        delta_team2 = self.calc_team_delta(team2_goal, trade_package_1['YEARS_REMAINING_ON_CONTRACT'].tolist(), delta_strength_t2, t2_win_now_score, delta_potential_t2, t2_future_score, delta_financial_t2, fit_score_t2)

        final_grade_t1 = self.grade(delta_team1, team1_goal)
        final_grade_t2 = self.grade(delta_team2, team2_goal)

        t1_superstar, t2_superstar = False, False

        for impact in trade_package_1['PLAYER_IMPACT'].tolist():
            if impact >= 0.43:
                t1_superstar = True
                break
        
        for impact in trade_package_2['PLAYER_IMPACT'].tolist():
            if impact >= 0.43:
                t2_superstar = True
                break
        
        if t1_superstar and not t2_superstar:
            if not (len(assets_2) >= 3 and gained_potential_t1 >= (lost_potential_t1 * 1.5)) and final_grade_t1 in ["A+", "A", "B+", "B", "B-", "C+", "C"]:
                final_grade_t1 = "C-"
        
        if t2_superstar and not t1_superstar:
            if not (len(assets_1) >= 3 and lost_potential_t1 >= (gained_potential_t1 * 1.5)) and final_grade_t2 in ["A+", "A", "B+", "B", "B-", "C+", "C"]:
                final_grade_t2 = "C-"

        return {
            team1: {'BEFORE': float(team1_strength), 'AFTER': float(team1_new_strength), 'STRENGTH_DELTA': float(delta_strength_t1), 'FINANCIAL_DELTA': float(delta_financial_t1), 'POTENTIAL_DELTA': float(delta_potential_t1), 'ROSTER_FIT_DELTA': float(fit_score_t1), 'DELTA': float(delta_team1), 'GRADE': final_grade_t1},
            team2: {'BEFORE': float(team2_strength), 'AFTER': float(team2_new_strength), 'STRENGTH_DELTA': float(delta_strength_t2), 'FINANCIAL_DELTA': float(delta_financial_t2), 'POTENTIAL_DELTA': float(delta_potential_t2), 'ROSTER_FIT_DELTA': float(fit_score_t2), 'DELTA': float(delta_team2), 'GRADE': final_grade_t2}
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

if __name__ == "__main__":
    simulate_trade = Trade()
    trade_result = simulate_trade.perform_trade("MIL", "MIA", ["Ryan Rollins"], ["Jaime Jaquez Jr."])
    print("\nTrade Result:")
    print(trade_result)