from pathlib import Path
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parent.parent
player_impacts = (
    ROOT_DIR
    / "Data"
    / "Processed Data"
    / "player_impact_v2.csv"
)
 
df = pd.read_csv(player_impacts)
 
current = df[df['SEASON'] == "2025-26"].copy()
 
teams = []
for team, roster in current.groupby('TEAM_ABBREVIATION'):
    best_players = roster.nlargest(10, 'PLAYER_IMPACT')
    impacts = best_players['PLAYER_IMPACT'].tolist()
    if len(impacts) < 2:
        continue

    star_players_score, roster_remaining = (impacts[0] + 0.85 * impacts[1] + 0.7 * impacts[2]), impacts[3:]
    if roster_remaining:
        depth_score = sum(roster_remaining) / len(roster_remaining)
    else:
        depth_score = 0
    
    team_strength = 0.8 * star_players_score + 0.2 * depth_score
    teams.append({
        'TEAM_ABBREVIATION': team,
        'STAR_PLAYERS_SCORE': star_players_score,
        'DEPTH_SCORE': depth_score,
        'TEAM_STRENGTH': team_strength
    })

projected_team_strengths = pd.DataFrame(teams)
projected_team_strengths = projected_team_strengths.sort_values('TEAM_STRENGTH', ascending = False).reset_index(drop = True)
 
print("\nTeam Strength Rankings:")
print(projected_team_strengths)

output_path = (
    ROOT_DIR
    / "Data"
    / "Processed Data"
    / "projected_team_strengths_v2.csv"
)

projected_team_strengths.to_csv(output_path, index=False)
print("\nFinished adding projected team strength scores to projected_team_strengths.csv.")