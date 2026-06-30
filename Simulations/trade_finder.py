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
        
        best_targets = (trades.groupby(['OPPOSING_TEAM', 'PLAYER_RECEIVED']).agg(AVG_TRADE_SCORE = ('TRADE_SCORE', 'mean'), AVG_TEAM_DELTA = ('TEAM_DELTA', 'mean'), BEST_TEAM_DELTA = ('TEAM_DELTA', 'max'), TRADE_COUNT = ('TEAM_DELTA', 'count')).reset_index())
        best_targets = best_targets.sort_values(by='AVG_TRADE_SCORE', ascending=False).reset_index(drop=True)

        best_assets = (trades.groupby(['PLAYER_SENT']).agg(AVG_TRADE_SCORE = ('TRADE_SCORE', 'mean'), AVG_TEAM_DELTA = ('TEAM_DELTA', 'mean'),  TRADE_COUNT = ('TEAM_DELTA', 'count')).reset_index())
        best_assets = best_assets.sort_values(by='AVG_TRADE_SCORE', ascending=False).reset_index(drop=True)

        print(f"\nBest trade targets for {team} with a minimum grade of {trade_grade}:\n")
        print(best_targets.head(10))

        print(f"\nBest trade assets for {team} with a minimum grade of {trade_grade}:\n")
        print(best_assets.head(10))

        return trades, best_targets, best_assets

    def find_optimal_trades(self, team, trade_grade = "C", min_impact = 0.2):
        print(f"\nFinding optimal trades for {team} with a minimum grade of {trade_grade}...")
        roster = self.current[self.current['TEAM_ABBREVIATION'] == team].copy()
        tradeable = roster[roster['PLAYER_IMPACT'] >= min_impact]['PLAYER_NAME'].tolist()
        packageable = roster[(roster['PLAYER_IMPACT'] >= min_impact) & (roster['PLAYER_IMPACT'] < 0.35)]['PLAYER_NAME'].tolist()

        rest_of_league = self.current[self.current['TEAM_ABBREVIATION'] != team]['TEAM_ABBREVIATION'].unique().tolist()

        potential_trades = []
        grades = ["F", "D", "C", "B", "A", "A+"]
        acceptable_grades = grades.index(trade_grade)
        checked_trades = 0

        pairs = list(itertools.combinations(packageable, 2))

        for opp in rest_of_league:
            opp_roster = self.current[self.current['TEAM_ABBREVIATION'] == opp].copy()
            opp_tradeable = opp_roster[opp_roster['PLAYER_IMPACT'] >= min_impact]['PLAYER_NAME'].tolist()
            for player in tradeable:
                for opp_player in opp_tradeable:
                    checked_trades += 1
                    outcome = self.trade_simulator.perform_trade(team, opp, [player], [opp_player], roster1 = roster, roster2 = opp_roster, silent = True)

                    if outcome is None:
                        continue
                    
                    delta_team, delta_opp = outcome[team]['DELTA'], outcome[opp]['DELTA']
                    grade_self, grade_opp = self.trade_simulator.grade(delta_team), self.trade_simulator.grade(delta_opp)

                    if grades.index(grade_self) >= acceptable_grades and grades.index(grade_opp) >= acceptable_grades:
                        reasonability = abs(delta_team - delta_opp)
                        trade_score = delta_team - (0.5 * reasonability)
                        potential_trades.append({
                            'TEAM': team,
                            'OPPOSING_TEAM': opp,
                            'PLAYER_SENT': player,
                            'PLAYER_RECEIVED': opp_player,
                            'TEAM_DELTA': delta_team,
                            'OPPOSING_TEAM_DELTA': delta_opp,
                            'TEAM_GRADE': grade_self,
                            'OPPOSING_TEAM_GRADE': grade_opp,
                            'FAIRNESS_SCORE': reasonability,
                            'TRADE_SCORE': trade_score
                        })
            
            for players in pairs:
                sent = list(players)
                for opp_player in opp_tradeable:
                    checked_trades += 1
                    outcome = self.trade_simulator.perform_trade(team, opp, sent, [opp_player], roster1 = roster, roster2 = opp_roster, silent = True)

                    if outcome is None:
                        continue

                    combination = " + ".join(sent)
                    delta_team, delta_opp = outcome[team]['DELTA'], outcome[opp]['DELTA']
                    grade_self, grade_opp = self.trade_simulator.grade(delta_team), self.trade_simulator.grade(delta_opp)

                    if grades.index(grade_self) >= acceptable_grades and grades.index(grade_opp) >= acceptable_grades:
                        reasonability = abs(delta_team - delta_opp)
                        trade_score = delta_team - (0.5 * reasonability)
                        potential_trades.append({
                            'TEAM': team,
                            'OPPOSING_TEAM': opp,
                            'PLAYER_SENT': combination,
                            'PLAYER_RECEIVED': opp_player,
                            'TEAM_DELTA': delta_team,
                            'OPPOSING_TEAM_DELTA': delta_opp,
                            'TEAM_GRADE': grade_self,
                            'OPPOSING_TEAM_GRADE': grade_opp,
                            'FAIRNESS_SCORE': reasonability,
                            'TRADE_SCORE': trade_score
                        })

        trades = pd.DataFrame(potential_trades)

        if not trades.empty:
            trades = trades.sort_values(by='TRADE_SCORE', ascending=False).reset_index(drop=True)
            print(f"\nCalculated {len(trades)} potential trades from {checked_trades} checked trades for {team} with a minimum grade of {trade_grade}.")
            print(f"Top 25 potential trades for {team} with a minimum grade of {trade_grade}:\n")
            print(trades[['OPPOSING_TEAM', 'PLAYER_SENT', 'PLAYER_RECEIVED', 'TEAM_GRADE', 'OPPOSING_TEAM_GRADE', 'TEAM_DELTA', 'FAIRNESS_SCORE', 'TRADE_SCORE']].head(25))
        else:
            print(f"\nNo potential trades found for {team} with a minimum grade of {trade_grade}.")
        
        return trades

    def save_to_csv(self, trades, output_path):
        trades.to_csv(output_path, index=False)
        print(f"\nSaved potential trades to {output_path}.")

if __name__ == "__main__":
    trade_finder = TradeFinder()
    team, trade_grade = "OKC", "B"
    min_impact = 0.2
    calculated, targets, assets = trade_finder.find_best_trade_targets(team, trade_grade, min_impact)

    if not calculated.empty:
        output_path = (
            Path(__file__).resolve().parent.parent
            / "Data"
            / "Processed Data"
            / f"potential_trades_{team}_{trade_grade}.csv"
        )
        trade_finder.save_to_csv(calculated, output_path)