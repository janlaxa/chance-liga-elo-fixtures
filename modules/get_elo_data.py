import requests
from io import StringIO
import pandas as pd

def get_elo_data(club):
    try:
        """Fetch ELO data from the API"""
        response = requests.get(f'http://api.clubelo.com/{club}')
        df = pd.read_csv(StringIO(response.text))
        latest_elo = df.iloc[-1]['Elo']
        latest_date = df.iloc[-1]['From']
        return latest_elo, latest_date, df
    except:
        return None, None, None