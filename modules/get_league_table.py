import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import sys

def get_league_table(season, club_mapping):
    url = f'https://www.transfermarkt.com/fortuna-liga/tabelle/wettbewerb/TS1/saison_id/{season}'
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print("Failed to retrieve data")
    soup = BeautifulSoup(response.text, 'html.parser')
    soup = soup.find("table", class_="items")

    match_rows = soup.find_all('tr')

    # Initialize an empty list to store the row indices and data
    row_data = []

    # Iterate over each match row and extract the index and data
    for index, row in enumerate(match_rows[1:], start=1):  # Skipping the header row
        columns = row.find_all('td')
        row_dict = {'index': index}
        for i, col in enumerate(columns):
            if i == 1:  # Extract the URL and regextract the number for the second column
                a_tag = col.find('a', href=True)
                if a_tag:
                    url = a_tag['href']
                    match = re.search(r'/verein/(\d+)/', url)
                    if match:
                        row_dict[f'col_{i}'] = match.group(1)
                    else:
                        row_dict[f'col_{i}'] = ''
                else:
                    row_dict[f'col_{i}'] = ''
            else:
                row_dict[f'col_{i}'] = col.get_text(strip=True)
        row_data.append(row_dict)


    # Create a dataframe from the list of row data
    df_indices = pd.DataFrame(row_data)
    df_indices = df_indices[['index','col_1','col_9']]
    column_names = ['position', 'tm_id', 'points']
    df_indices.columns = column_names

    df_indices
    return df_indices

    # Extract the club names and URLs

def get_home_league_table(season, club_mapping):
    url = f'https://www.transfermarkt.com/fortuna-liga/heimtabelle/wettbewerb/TS1/saison_id/{season}'
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print("Failed to retrieve data")
    soup = BeautifulSoup(response.text, 'html.parser')
    soup = soup.find("table", class_="items")

    match_rows = soup.find_all('tr')

    # Initialize an empty list to store the row indices and data
    row_data = []

    # Iterate over each match row and extract the index and data
    for index, row in enumerate(match_rows[1:], start=1):  # Skipping the header row
        columns = row.find_all('td')
        row_dict = {'index': index}
        for i, col in enumerate(columns):
            if i == 1:  # Extract the URL and regextract the number for the second column
                a_tag = col.find('a', href=True)
                if a_tag:
                    url = a_tag['href']
                    match = re.search(r'/verein/(\d+)/', url)
                    if match:
                        row_dict[f'col_{i}'] = match.group(1)
                    else:
                        row_dict[f'col_{i}'] = ''
                else:
                    row_dict[f'col_{i}'] = ''
            else:
                row_dict[f'col_{i}'] = col.get_text(strip=True)
        row_data.append(row_dict)


    # Create a dataframe from the list of row data
    df_indices = pd.DataFrame(row_data)
    df_indices = df_indices[['index','col_1','col_9']]
    column_names = ['position', 'tm_id', 'points']
    df_indices.columns = column_names

    df_indices
    return df_indices

def get_away_league_table(season, club_mapping):
    url = f'https://www.transfermarkt.com/fortuna-liga/gasttabelle/wettbewerb/TS1/saison_id/{season}'
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print("Failed to retrieve data")
    soup = BeautifulSoup(response.text, 'html.parser')
    soup = soup.find("table", class_="items")

    match_rows = soup.find_all('tr')

    # Initialize an empty list to store the row indices and data
    row_data = []

    # Iterate over each match row and extract the index and data
    for index, row in enumerate(match_rows[1:], start=1):  # Skipping the header row
        columns = row.find_all('td')
        row_dict = {'index': index}
        for i, col in enumerate(columns):
            if i == 1:  # Extract the URL and regextract the number for the second column
                a_tag = col.find('a', href=True)
                if a_tag:
                    url = a_tag['href']
                    match = re.search(r'/verein/(\d+)/', url)
                    if match:
                        row_dict[f'col_{i}'] = match.group(1)
                    else:
                        row_dict[f'col_{i}'] = ''
                else:
                    row_dict[f'col_{i}'] = ''
            else:
                row_dict[f'col_{i}'] = col.get_text(strip=True)
        row_data.append(row_dict)


    # Create a dataframe from the list of row data
    df_indices = pd.DataFrame(row_data)
    df_indices = df_indices[['index','col_1','col_9']]
    column_names = ['position', 'tm_id', 'points']
    df_indices.columns = column_names

    df_indices
    return df_indices