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
            case _ if delta >= 0.01:
                return "B"
            case _ if delta >= -0.01:
                return "C"
            case _ if delta >= -0.03:
                return "D"
            case _:
                return "F"

    def perform_trade(self, team1, team2, players_1, players_2):
        print(f"\nSimulating trade between {team1} and {team2}...")
        print(f"{team1} send the following player(s) to {team2}: {', '.join(players_1)}")
        print(f"{team2} send the following player(s) to {team1}: {', '.join(players_2)}")

        team1_roster = self.current[self.current['TEAM_ABBREVIATION'] == team1].copy()
        team2_roster = self.current[self.current['TEAM_ABBREVIATION'] == team2].copy()

        team1_strength = self.calculate_team_strength(team1_roster['PLAYER_IMPACT'].tolist())
        team2_strength = self.calculate_team_strength(team2_roster['PLAYER_IMPACT'].tolist())

        package_1 = team1_roster[team1_roster['PLAYER_NAME'].isin(players_1)].copy()
        package_2 = team2_roster[team2_roster['PLAYER_NAME'].isin(players_2)].copy()

        if (len(package_1) == 0) or (len(package_2) == 0):
            print("Error: One of the teams does not have the specified player(s).")
            return None
        
        if (len(package_1) != len(players_1)) or (len(package_2) != len(players_2)):
            print("Error: One of the teams does not have all the specified player(s).")
            return None
        
        team1_new_strength = self.calculate_team_strength(team1_roster[~team1_roster['PLAYER_NAME'].isin(players_1)]['PLAYER_IMPACT'].tolist() + package_2['PLAYER_IMPACT'].tolist())
        team2_new_strength = self.calculate_team_strength(team2_roster[~team2_roster['PLAYER_NAME'].isin(players_2)]['PLAYER_IMPACT'].tolist() + package_1['PLAYER_IMPACT'].tolist())

        delta_team1, delta_team2 = team1_new_strength - team1_strength, team2_new_strength - team2_strength

        print(f"\n{team1} strength change: {delta_team1:.4f} (from {team1_strength:.4f} to {team1_new_strength:.4f})")
        print(f"{team2} strength change: {delta_team2:.4f} (from {team2_strength:.4f} to {team2_new_strength:.4f})")

        print(f"\n{team1} trade grade: {self.grade(delta_team1)}")
        print(f"{team2} trade grade: {self.grade(delta_team2)}")

        return {
            team1: {'BEFORE': team1_strength, 'AFTER': team1_new_strength, 'DELTA': delta_team1},
            team2: {'BEFORE': team2_strength, 'AFTER': team2_new_strength, 'DELTA': delta_team2}
        }

# if __name__ == "__main__":
#     simulate_trade = Trade()
#     trade_result = simulate_trade.perform_trade("MIL", "MIA", ["Giannis Antetokounmpo", "Bobby Portis"], ["Tyler Herro", "Kel'el Ware", "Jaime Jaquez Jr.", "Kasparas Jakučionis"])
#     print("\nTrade Result:")
#     print(trade_result)