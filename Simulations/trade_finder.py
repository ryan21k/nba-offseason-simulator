from pathlib import Path
from trade_simulation import Trade
import pandas as pd
import itertools

class TradeFinder:
    def __init__(self):
        self.trade_simulator = Trade()
        self.current = self.trade_simulator.current

    def find_best_trade_targets(self, team, trade_grade = "C", min_impact = 0.2):
        trades = self.find_optimal_trades(team, trade_grade, min_impact)
        if trades.empty:
            return trades, pd.DataFrame(), pd.DataFrame()
        
        best_targets = (trades.groupby(['OPPOSING_TEAM', 'ASSETS_RECEIVED']).agg(AVG_TRADE_SCORE = ('TRADE_SCORE', 'mean'), AVG_TEAM_DELTA = ('TEAM_DELTA', 'mean'), BEST_TEAM_DELTA = ('TEAM_DELTA', 'max'), TRADE_COUNT = ('TEAM_DELTA', 'count')).reset_index())
        best_targets = best_targets.sort_values(by='AVG_TRADE_SCORE', ascending=False).reset_index(drop=True)

        best_assets = (trades.groupby(['ASSETS_SENT']).agg(AVG_TRADE_SCORE = ('TRADE_SCORE', 'mean'), AVG_TEAM_DELTA = ('TEAM_DELTA', 'mean'),  TRADE_COUNT = ('TEAM_DELTA', 'count')).reset_index())
        best_assets = best_assets.sort_values(by='AVG_TRADE_SCORE', ascending=False).reset_index(drop=True)

        print(f"\nBest trade targets for {team} with a minimum grade of {trade_grade}:\n")
        print(best_targets.head(10))

        print(f"\nBest trade assets for {team} with a minimum grade of {trade_grade}:\n")
        print(best_assets.head(10))

        return trades, best_targets, best_assets

    def find_optimal_trades(self, team, trade_grade = "C", min_impact = 0.2):
        print(f"\nFinding optimal trades for {team} with a minimum grade of {trade_grade}...")
        roster = self.current[self.current['TEAM_ABBREVIATION'] == team].copy()
        
        star_players = roster[roster['PLAYER_IMPACT'] >= 0.4]['PLAYER_NAME'].tolist()
        roster_depth = roster[(roster['PLAYER_IMPACT'] >= min_impact) & (roster['PLAYER_IMPACT'] < 0.4)]['PLAYER_NAME'].tolist()

        rest_of_league = self.current[self.current['TEAM_ABBREVIATION'] != team]['TEAM_ABBREVIATION'].unique().tolist()

        salary_search, impact_search = {}, {}

        for index, row in self.current.iterrows():
            player = row['PLAYER_NAME']
            salary, impact = row['CLEAN_SALARY'], row['PLAYER_IMPACT']
            salary_search[player] = salary
            impact_search[player] = impact

        potential_trades = []
        grades = ["F", "D", "C-", "C", "C+", "B-", "B", "B+", "A", "A+"]
        acceptable_grades = grades.index(trade_grade)
        checked_trades = 0

        def create_trade_package(stars, depth, team_abbreviation):
            trade_packages = []
            players = stars + depth
            
            for player in players:
                trade_packages.append([player])
            
            for combination in itertools.combinations(players, 2):
                if combination[0] in stars and combination[1] in stars:
                    continue
                trade_packages.append(list(combination))

            for combination in itertools.combinations(depth, 3):
                trade_packages.append(list(combination))
            
            draft_packages = []
            picks = [f"2027 {team_abbreviation} 1st (unprotected)", f"2029 {team_abbreviation} 1st (top3 protected)"]

            for package in trade_packages:
                draft_packages.append(package)
                draft_packages.append(package + [picks[0]])
                draft_packages.append(package + [picks[1]])
                draft_packages.append(package + picks)
            return draft_packages

        team_package = create_trade_package(star_players, roster_depth, team)

        for opp in rest_of_league:
            opp_roster = self.current[self.current['TEAM_ABBREVIATION'] == opp]
            opp_stars = opp_roster[opp_roster['PLAYER_IMPACT'] >= 0.4]['PLAYER_NAME'].tolist()
            opp_franchise_players = opp_roster[opp_roster['PLAYER_IMPACT'] >= 0.43]['PLAYER_NAME'].tolist()

            filtered_stars = []

            for player in opp_stars:
                if player not in opp_franchise_players:
                    filtered_stars.append(player)
            opp_stars = filtered_stars

            opp_depth = opp_roster[(opp_roster['PLAYER_IMPACT'] >= min_impact) & (opp_roster['PLAYER_IMPACT'] < 0.4)]['PLAYER_NAME'].tolist()

            opp_package = create_trade_package(opp_stars, opp_depth, opp)
            for sending in team_package:
                for getting in opp_package:
                    if len(sending) > 4 or len(getting) > 4:
                        continue

                    sending_star = bool(set(sending) & set(star_players))
                    receiving_star = bool(set(getting) & set(opp_stars))

                    if not sending_star and not receiving_star:
                        continue

                    if set(sending) & set(getting):
                        continue

                    outgoing_salary, incoming_salary = 0, 0
                    for player in sending:
                        outgoing_salary += salary_search.get(player, 0)
                    
                    for player in getting:
                        incoming_salary += salary_search.get(player, 0)
                    
                    if abs(outgoing_salary - incoming_salary) > 5000000:
                        smaller = min(outgoing_salary, incoming_salary) + 1
                        if (max(outgoing_salary, incoming_salary) / smaller) > 1.25:
                            continue
                    
                    outgoing_impact, incoming_impact = 0, 0
                    for player in sending:
                        outgoing_impact += impact_search.get(player, 0)
                    
                    for player in getting:
                        incoming_impact += impact_search.get(player, 0)
                    
                    if sending_star and (incoming_impact < outgoing_impact * 0.7):
                        continue

                    checked_trades += 1
                    outcome = self.trade_simulator.perform_trade(team, opp, sending, getting, roster1 = roster, roster2 = opp_roster, silent = True)

                    if outcome is None:
                        continue
                    
                    delta_team, delta_opp = outcome[team]['DELTA'], outcome[opp]['DELTA']
                    grade_self, grade_opp = outcome[team]['GRADE'], outcome[opp]['GRADE']

                    if outcome[team]['ROSTER_FIT_DELTA'] < -0.05:
                        continue

                    if grades.index(grade_self) >= acceptable_grades and grades.index(grade_opp) >= acceptable_grades:
                        reasonability = abs(delta_team - delta_opp)
                        trade_score = delta_team - (0.5 * reasonability)
                        potential_trades.append({
                            'TEAM': team,
                            'OPPOSING_TEAM': opp,
                            'ASSETS_SENT': " + ".join(sending),
                            'ASSETS_RECEIVED': " + ".join(getting),
                            'TEAM_DELTA': delta_team,
                            'STRENGTH_DELTA': outcome[team]['STRENGTH_DELTA'],
                            'FINANCIAL_DELTA': outcome[team]['FINANCIAL_DELTA'],
                            'POTENTIAL_DELTA': outcome[team]['POTENTIAL_DELTA'],
                            'ROSTER_FIT_DELTA': outcome[team]['ROSTER_FIT_DELTA'],
                            'OPPOSING_TEAM_DELTA': delta_opp,
                            'TEAM_GRADE': grade_self,
                            'OPPOSING_TEAM_GRADE': grade_opp,
                            'FAIRNESS_SCORE': reasonability,
                            'TRADE_SCORE': trade_score
                        })

        trades = pd.DataFrame(potential_trades)

        if not trades.empty:
            trades = trades.sort_values(by='TRADE_SCORE', ascending=False).reset_index(drop=True)
            blockbuster_trades = trades[(trades['TEAM_DELTA'].abs() >= 0.15)].reset_index(drop = True)
            print(f"\nCalculated {len(trades)} potential trades from {checked_trades} checked trades for {team} with a minimum grade of {trade_grade}.")
            print(f"Top 25 potential trades for {team} with a minimum grade of {trade_grade}:\n")
            print(blockbuster_trades[['OPPOSING_TEAM', 'ASSETS_SENT', 'ASSETS_RECEIVED', 'TEAM_GRADE', 'OPPOSING_TEAM_GRADE', 'TEAM_DELTA', 'STRENGTH_DELTA', 'FINANCIAL_DELTA', 'POTENTIAL_DELTA', 'ROSTER_FIT_DELTA', 'TRADE_SCORE']].head(25))
        else:
            print(f"\nNo potential trades found for {team} with a minimum grade of {trade_grade}.")
        
        return trades

    def save_to_csv(self, trades, output_path):
        trades.to_csv(output_path, index=False)
        print(f"\nSaved potential trades to {output_path}.")

if __name__ == "__main__":
    trade_finder = TradeFinder()
    team, trade_grade = "MIL", "B"
    min_impact = 0.3
    calculated, targets, assets = trade_finder.find_best_trade_targets(team, trade_grade, min_impact)

    if not calculated.empty:
        output_path = (
            Path(__file__).resolve().parent.parent
            / "Data"
            / "Processed Data"
            / f"potential_trades_{team}_{trade_grade}.csv"
        )
        trade_finder.save_to_csv(calculated, output_path)