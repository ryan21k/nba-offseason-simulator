from pathlib import Path
from bs4 import BeautifulSoup
from curl_cffi import requests
import pandas as pd
import time, os

ROOT_DIR = Path(__file__).resolve().parent.parent
salary_url = "https://www.basketball-reference.com/contracts/players.html"

print("Scraping NBA Players' Salary Data ...")
time.sleep(1)
response = requests.get(salary_url, impersonate = "chrome120", timeout = 30)

if response.status_code == 200:
    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.find('table', {'id': 'player-contracts'})
    
    if table:
        rows = []
        seen = set()

        for tr in table.find('tbody').find_all('tr'):
            if 'thead' in tr.get('class', []):
                continue
            player_data = tr.find('td', {'data-stat': 'player'})
            if not player_data:
                continue
            player_id = player_data.get('data-append-csv', '')
            if not player_id or player_id in seen:
                continue
            seen.add(player_id)

            def get_val(stat):
                td = tr.find(['td', 'th'], {'data-stat': stat})
                if td:
                    return td.get_text(strip = True)
                return ''

            rows.append({'PLAYER_NAME': get_val('player'), 'TEAM_ABBREVIATION': get_val('team_id'), '2025_26_SALARY':     get_val('y1'), '2026_27_SALARY':     get_val('y2'), '2027_28_SALARY':     get_val('y3'), '2028_29_SALARY':     get_val('y4'), '2029_30_SALARY':     get_val('y5'), '2030_31_SALARY':     get_val('y6'), 'GUARANTEED_SALARY':  get_val('remain_gtd'),})

        df = pd.DataFrame(rows)
        os.makedirs("../Processed Data", exist_ok = True)
        df.to_csv("../Processed Data/player_salary_data.csv", index = False)
        print("Finished adding player salary content to player_salary_data.csv")
    else:
        print("Error: Could not find the 'player_contracts' table on the page.")
else:
    print(f"Error: Failed to fetch data. Status code: {response.status_code}")
time.sleep(1)