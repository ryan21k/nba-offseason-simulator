from bs4 import BeautifulSoup
import pandas as pd
import requests
import time
import os
import logging

OUTPUT_DIRECTORY = "Data/Standings" #path that stores the csv files

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

nba_team_data = [] #list that will store all 30 nba teams data

for year in range(2015, 2026):
    url = f"https://www.basketball-reference.com/leagues/NBA_{year}.html"
    print(f"Scraping the NBA {year - 1}-{str(year)[-2:]} season...")
    
    