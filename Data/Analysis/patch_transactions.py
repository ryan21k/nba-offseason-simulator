from pathlib import Path
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parent.parent

team_dataset = (
    ROOT_DIR 
    / "Processed Data" 
    / "player_team_dataset.csv"
)

output_path = (
    ROOT_DIR 
    / "Processed Data"
    / "player_team_dataset_2026_27.csv"
)

METADATA_COLS = ["Unnamed: 0", "PLAYER_ID", "PLAYER_NAME", "TEAM_ABBREVIATION", "SEASON"]

UPDATED_TRADES_AND_SIGNINGS = [
    {"PLAYER_NAME": "Lugentz Dort", "NEW_TEAM": "ATL"},
    {"PLAYER_NAME": "Aaron Wiggins", "NEW_TEAM": "ATL"},
    {"PLAYER_NAME": "Ryan Nembhard", "NEW_TEAM": "ATL"},
    {"PLAYER_NAME": "Devin Carter", "NEW_TEAM": "ATL"},
    {"PLAYER_NAME": "Paul George", "NEW_TEAM": "BOS"},
    {"PLAYER_NAME": "Mike Conley", "NEW_TEAM": "BOS"},
    {"PLAYER_NAME": "Mitchell Robinson", "NEW_TEAM": "BOS"},
    {"PLAYER_NAME": "Julius Randle", "NEW_TEAM": "BKN"},
    {"PLAYER_NAME": "Naz Reid", "NEW_TEAM": "CHA"},
    {"PLAYER_NAME": "Grayson Allen", "NEW_TEAM": "CHA"},
    {"PLAYER_NAME": "Royce O'Neal", "NEW_TEAM": "CHA"},
    {"PLAYER_NAME": "Dorian Finney-Smith", "NEW_TEAM": "CHA"},
    {"PLAYER_NAME": "Nic Claxton", "NEW_TEAM": "CHI"},
    {"PLAYER_NAME": "Norman Powell", "NEW_TEAM": "CHI"},
    {"PLAYER_NAME": "Olivier Sarr", "NEW_TEAM": "CLE"},
    {"PLAYER_NAME": "Zaccharie Risacher", "NEW_TEAM": "DAL"},
    {"PLAYER_NAME": "Marcus Sasser", "NEW_TEAM": "DAL"},
    {"PLAYER_NAME": "Santi Aldama", "NEW_TEAM": "DAL"},
    {"PLAYER_NAME": "Isaiah Joe", "NEW_TEAM": "DET"},
    {"PLAYER_NAME": "John Collins", "NEW_TEAM": "DET"},
    {"PLAYER_NAME": "Taurean Prince", "NEW_TEAM": "DET"},
    {"PLAYER_NAME": "Gary Harris", "NEW_TEAM": "DET"},
    {"PLAYER_NAME": "Charles Bassey", "NEW_TEAM": "GSW"},
    {"PLAYER_NAME": "Marcus Smart", "NEW_TEAM": "HOU"},
    {"PLAYER_NAME": "Bogdan Bogdanović", "NEW_TEAM": "HOU"},
    {"PLAYER_NAME": "Kelly Oubre Jr.", "NEW_TEAM": "IND"},
    {"PLAYER_NAME": "Larry Nance Jr.", "NEW_TEAM": "IND"},
    {"PLAYER_NAME": "Brandon Ingram", "NEW_TEAM": "LAC"},
    {"PLAYER_NAME": "Gradey Dick", "NEW_TEAM": "LAC"},
    {"PLAYER_NAME": "Rui Hachimura", "NEW_TEAM": "LAC"},
    {"PLAYER_NAME": "Walker Kessler", "NEW_TEAM": "LAL"},
    {"PLAYER_NAME": "Jaden Hardy", "NEW_TEAM": "LAL"},
    {"PLAYER_NAME": "Collin Sexton", "NEW_TEAM": "LAL"},
    {"PLAYER_NAME": "Quentin Grimes", "NEW_TEAM": "LAL"},
    {"PLAYER_NAME": "Matisse Thybulle", "NEW_TEAM": "LAL"},
    {"PLAYER_NAME": "Ziaire Williams", "NEW_TEAM": "LAL"},
    {"PLAYER_NAME": "Sandro Mamukelashvili", "NEW_TEAM": "LAL"},
    {"PLAYER_NAME": "Kevon Looney", "NEW_TEAM": "LAL"},
    {"PLAYER_NAME": "Jerami Grant", "NEW_TEAM": "MEM"},
    {"PLAYER_NAME": "Kris Murray", "NEW_TEAM": "MEM"},
    {"PLAYER_NAME": "AJ Johnson", "NEW_TEAM": "MEM"},
    {"PLAYER_NAME": "Isaiah Stewart", "NEW_TEAM": "MEM"},
    {"PLAYER_NAME": "D'Angelo Russell", "NEW_TEAM": "MEM"},
    {"PLAYER_NAME": "Quinten Post", "NEW_TEAM": "MEM"},
    {"PLAYER_NAME": "Giannis Antetokounmpo", "NEW_TEAM": "MIA"},
    {"PLAYER_NAME": "Bobby Portis", "NEW_TEAM": "MIA"},
    {"PLAYER_NAME": "Tim Hardaway Jr.", "NEW_TEAM": "MIA"},
    {"PLAYER_NAME": "Tyler Herro", "NEW_TEAM": "MIL"},
    {"PLAYER_NAME": "Jaime Jaquez Jr.", "NEW_TEAM": "MIL"},
    {"PLAYER_NAME": "Kasparas Jakučionis", "NEW_TEAM": "MIL"},
    {"PLAYER_NAME": "Kel'el Ware", "NEW_TEAM": "MIL"},
    {"PLAYER_NAME": "Caris LeVert", "NEW_TEAM": "MIL"},
    {"PLAYER_NAME": "LaMelo Ball", "NEW_TEAM": "MIN"},
    {"PLAYER_NAME": "Josh Green", "NEW_TEAM": "MIN"},
    {"PLAYER_NAME": "Mouhamed Gueye", "NEW_TEAM": "MIN"},
    {"PLAYER_NAME": "Trey Lyles", "NEW_TEAM": "MIN"},
    {"PLAYER_NAME": "Andre Drummond", "NEW_TEAM": "NYK"},
    {"PLAYER_NAME": "Moussa Cisse", "NEW_TEAM": "NYK"},
    {"PLAYER_NAME": "Nikola Vučević", "NEW_TEAM": "ORL"},
    {"PLAYER_NAME": "Jaylen Brown", "NEW_TEAM": "PHI"},
    {"PLAYER_NAME": "Anfernee Simons", "NEW_TEAM": "PHI"},
    {"PLAYER_NAME": "Dean Wade", "NEW_TEAM": "PHI"},
    {"PLAYER_NAME": "Ariel Hukporti", "NEW_TEAM": "PHI"},
    {"PLAYER_NAME": "Caleb Love", "NEW_TEAM": "PHI"},
    {"PLAYER_NAME": "Rayan Rupert", "NEW_TEAM": "PHI"},
    {"PLAYER_NAME": "Miles Bridges", "NEW_TEAM": "PHX"},
    {"PLAYER_NAME": "Luke Kennard", "NEW_TEAM": "PHX"},
    {"PLAYER_NAME": "Haywood Highsmith", "NEW_TEAM": "PHX"},
    {"PLAYER_NAME": "Ja Morant", "NEW_TEAM": "POR"},
    {"PLAYER_NAME": "Branden Carlson", "NEW_TEAM": "POR"},
    {"PLAYER_NAME": "Micah Potter", "NEW_TEAM": "POR"},
    {"PLAYER_NAME": "Jonathan Mogbo", "NEW_TEAM": "SAC"},
    {"PLAYER_NAME": "Tobias Harris", "NEW_TEAM": "SAS"},
    {"PLAYER_NAME": "Kawhi Leonard", "NEW_TEAM": "TOR"},
    {"PLAYER_NAME": "Kyle Anderson", "NEW_TEAM": "TOR"},
    {"PLAYER_NAME": "Josh Okogie", "NEW_TEAM": "UTA"},
    {"PLAYER_NAME": "Jaxson Hayes", "NEW_TEAM": "UTA"},
    {"PLAYER_NAME": "Mo Bamba", "NEW_TEAM": "UTA"},
    {"PLAYER_NAME": "Deandre Ayton", "NEW_TEAM": "WAS"},
    {"PLAYER_NAME": "Khris Middleton", "NEW_TEAM": "WAS"},
    {"PLAYER_NAME": "Cam Whitmore", "NEW_TEAM": "WAS"}
]

teams_df = pd.read_csv(team_dataset)
new_team_rows = []

for update in UPDATED_TRADES_AND_SIGNINGS:
    player_name = update.get("PLAYER_NAME")
    if not player_name:
        continue

    new_team = update.get("NEW_TEAM")
    if new_team:
        record_exists_26 = (teams_df["PLAYER_NAME"].str.lower() == player_name.lower()) & (teams_df["SEASON"] == "2026-27")

        if record_exists_26.any():
            teams_df.loc[record_exists_26, "TEAM_ABBREVIATION"] = new_team
            print(f"Updated {player_name} -> {new_team} for 2026-27 season.")
        else:
            players = teams_df[teams_df["PLAYER_NAME"].str.lower() == player_name.lower()]

            if not players.empty:
                recent = players.iloc[-1].copy()
                recent["SEASON"] = "2026-27"
                recent["TEAM_ABBREVIATION"] = new_team
                new_team_rows.append(recent)
                print(f"Added {player_name} -> {new_team} for 2026-27 season.")

if new_team_rows:
    new_rows = pd.DataFrame(new_team_rows)
    teams_df = pd.concat([teams_df, new_rows], ignore_index = True)

df_2025_26 = teams_df[teams_df["SEASON"] == "2025-26"].copy()
existing_26_27 = set(teams_df[teams_df["SEASON"] == "2026-27"]["PLAYER_NAME"].str.lower().unique())

leftover_players = ~df_2025_26["PLAYER_NAME"].str.lower().isin(existing_26_27)
leftover_rows = df_2025_26[leftover_players].copy()

leftover_rows["SEASON"] = "2026-27"
teams_df = pd.concat([teams_df, leftover_rows], ignore_index = True)

stat_columns = teams_df.select_dtypes(include="number").columns.difference(METADATA_COLS)
teams_df.loc[teams_df["SEASON"] == "2026-27", stat_columns] = 0
df_26_27 = teams_df[teams_df["SEASON"] == "2026-27"].copy()

teams_df.to_csv(team_dataset, index = False)
df_26_27.to_csv(output_path, index = False)
print("Successfully added NBA 26/27 roster data to player_team_dataset_2026_27.csv")