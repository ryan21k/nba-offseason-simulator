from pathlib import Path
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parent.parent
player_impacts = (
    ROOT_DIR
    / "Data"
    / "Processed Data"
    / "player_impact_v2.csv"
)

class Trade:
    def __init__(self):
        self.player_impacts = pd.read_csv(player_impacts)
        self.current = self.player_impacts[self.player_impacts['SEASON'] == "2025-26"].copy()
    
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
            case _ if delta >= 0:
                return "C"
            case _ if delta >= -0.015:
                return "D"
            case _:
                return "F"

    def evaluate_trade(self, team1, team2, players_1, players_2):
        roster1 = self.current[self.current['TEAM_ABBREVIATION'] == team1].copy()
        roster2 = self.current[self.current['TEAM_ABBREVIATION'] == team2].copy()

        team1_strength = self.calculate_team_strength(roster1['PLAYER_IMPACT'].tolist())
        team2_strength = self.calculate_team_strength(roster2['PLAYER_IMPACT'].tolist())

        trade_package_1 = roster1[roster1['PLAYER_NAME'].isin(players_1)]
        trade_package_2 = roster2[roster2['PLAYER_NAME'].isin(players_2)]

        if (len(trade_package_1) == 0) or (len(trade_package_2) == 0):
            print("Error: One of the teams does not have the specified player(s).")
            return None
        
        if (len(trade_package_1) != len(players_1)) or (len(trade_package_2) != len(players_2)):
            print("Error: One of the teams does not have all the specified player(s).")
            return None
        
        team1_new_strength = self.calculate_team_strength(roster1[~roster1['PLAYER_NAME'].isin(players_1)]['PLAYER_IMPACT'].tolist() + trade_package_2['PLAYER_IMPACT'].tolist())
        team2_new_strength = self.calculate_team_strength(roster2[~roster2['PLAYER_NAME'].isin(players_2)]['PLAYER_IMPACT'].tolist() + trade_package_1['PLAYER_IMPACT'].tolist())

        delta_team1, delta_team2 = team1_new_strength - team1_strength, team2_new_strength - team2_strength

        return {
            team1: {'BEFORE': team1_strength, 'AFTER': team1_new_strength, 'DELTA': delta_team1, 'GRADE': self.grade(delta_team1)},
            team2: {'BEFORE': team2_strength, 'AFTER': team2_new_strength, 'DELTA': delta_team2, 'GRADE': self.grade(delta_team2)}
        }

    def perform_trade(self, team1, team2, players_1, players_2):
        print(f"\nSimulating trade between {team1} and {team2}...")
        print(f"{team1} send the following player(s) to {team2}: {', '.join(players_1)}")
        print(f"{team2} send the following player(s) to {team1}: {', '.join(players_2)}")

        trade_eval = self.evaluate_trade(team1, team2, players_1, players_2)
        if trade_eval is None:
            print("Trade evaluation failed. Please check the player names and try again.")
            return None

        print(f"\n{team1} strength change: {trade_eval[team1]['DELTA']:.4f}")
        print(f"{team2} strength change: {trade_eval[team2]['DELTA']:.4f}")

        print(f"\n{team1} trade grade: {trade_eval[team1]['GRADE']}")
        print(f"{team2} trade grade: {trade_eval[team2]['GRADE']}")

        return trade_eval

# if __name__ == "__main__":
#     simulate_trade = Trade()
#     trade_result = simulate_trade.perform_trade("MIL", "MIA", ["Giannis Antetokounmpo", "Bobby Portis"], ["Tyler Herro", "Kel'el Ware", "Jaime Jaquez Jr.", "Kasparas Jakučionis"])
#     print("\nTrade Result:")
#     print(trade_result)