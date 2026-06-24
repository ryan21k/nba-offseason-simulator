from pathlib import Path
from trade_simulation import Trade
import pandas as pd

class TradeFinder:
    def __init__(self):
        self.trade_simulator = Trade()
        self.current = self.trade_simulator.current

    def find_optimal_trades(self, team, trade_grade = "C"):
        print(f"\nFinding optimal trades for {team} with a minimum grade of {trade_grade}...")
        roster = self.current[self.current['TEAM_ABBREVIATION'] == team]['PLAYER_NAME'].tolist()
        rest_of_league = self.current[self.current['TEAM_ABBREVIATION'] != team]['TEAM_ABBREVIATION'].tolist()

        potential_trades = []
        grades = ["F", "D", "C", "B", "A", "A+"]
        acceptable_grades = grades.index(trade_grade)

        for opp in rest_of_league:
            opp_roster = self.current[self.current['TEAM_ABBREVIATION'] == opp]['PLAYER_NAME'].tolist()
            for player in roster[:8]:
                for opp_player in opp_roster[:8]:
                    outcome = self.trade_simulator.perform_trade(team, opp, [player], [opp_player])

                    if outcome is None:
                        continue
                    
                    grade_self, grade_opp = self.trade_simulator.grade(outcome[team]['DELTA']), self.trade_simulator.grade(outcome[opp]['DELTA'])

                    if grades.index(grade_self) >= acceptable_grades and grades.index(grade_opp) >= acceptable_grades:
                        potential_trades.append({
                            'OPPOSING_TEAM': opp,
                            'PLAYER_SENT': player,
                            'PLAYER_RECEIVED': opp_player,
                            'TEAM_DELTA': outcome[team]['DELTA'],
                            'OPPOSING_TEAM_DELTA': outcome[opp]['DELTA'],
                            'TEAM_GRADE': grade_self,
                            'OPPOSING_TEAM_GRADE': grade_opp
                        })
        trades = pd.DataFrame(potential_trades)

        if not trades.empty:
            trades = trades.sort_values(by='TEAM_DELTA', ascending=False).reset_index(drop=True)
            print(f"\nCalculated {len(trades)} potential trades for {team} with a minimum grade of {trade_grade}.")
            print(trades[['OPPOSING_TEAM', 'PLAYER_SENT', 'PLAYER_RECEIVED', 'TEAM_GRADE', 'OPPOSING_TEAM_GRADE']])
        else:
            print(f"\nNo potential trades found for {team} with a minimum grade of {trade_grade}.")
        
        return trades

# if __name__ == "__main__":
#     trade_finder = TradeFinder()
#     team_to_analyze = "MIL"
#     minimum_grade = "C"
#     trade_finder.find_optimal_trades(team_to_analyze, minimum_grade)