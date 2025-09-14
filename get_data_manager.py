import requests
import json
from os import path
from datetime import datetime
from dateutil.relativedelta import relativedelta
from api_config import API_KEY
BASE_URL = "https://www.alphavantage.co/query?"


def recuperer_les_datas(date_debut,date_fin,function, symbol, interval, adjusted, extended_hours, outputsize, datatype):
    date_debut_dt = datetime.strptime(date_debut, '%Y-%m')
    date_fin_dt = datetime.strptime(date_fin, '%Y-%m')
    nombre_mois = (date_fin_dt.year - date_debut_dt.year) * 12 + (date_fin_dt.month - date_debut_dt.month)    
    current_date = date_debut_dt
    for _ in range(nombre_mois + 1):  # +1 si tu veux inclure le mois de fin
        recuperer_la_data(function, symbol, interval, adjusted, extended_hours, current_date.strftime('%Y-%m') , outputsize, datatype)
        current_date += relativedelta(months=1)

def recuperer_la_data(function, symbol, interval, adjusted, extended_hours, month, outputsize, datatype):
    data_filename = symbol + interval + ".json"
    if path.exists(data_filename) : 
        print(f"File {data_filename} already exists. Data not overwritten.")
        with open(data_filename, 'r') as f:
            data = json.load(f)
        data_complete = list(data.keys())[1]
        data_start = list(data[data_complete].keys())[-1]
        data_start = datetime.strptime(data_start, '%Y-%m-%d %H:%M:%S')
        data_start_month_str = data_start.strftime('%Y-%m')
        print(f"Data starts at {data_start_month_str}")
        data_end = list(data[data_complete].keys())[0]
        data_end = datetime.strptime(data_end, '%Y-%m-%d %H:%M:%S')
        data_end_month_str = data_end.strftime('%Y-%m')
        print(f"Data ends at {data_end_month_str}")
        data_start_month_dt = datetime.strptime(data_start_month_str, '%Y-%m')
        data_end_month_dt = datetime.strptime(data_end_month_str, '%Y-%m')
        month_dt = datetime.strptime(month, '%Y-%m')
        
    if not path.exists(data_filename) or data_start_month_dt < month_dt or month_dt < data_end_month_dt : #mettre la date du debut et de la fin des donnees que l'on veut
        try:
            url = BASE_URL + "function=" + function + "&symbol="+symbol+"&interval="+interval+"&adjusted="+adjusted+"&extended_hours="+extended_hours+"&month="+month+"&outputsize="+outputsize+"&datatype="+datatype+"&apikey=" + API_KEY
            r = requests.get(url)
            data = r.json()
        except: 
            print("Error in API call, possibly due to network issues or invalid response.")
            return None
        if not path.exists(data_filename):
            print(f"File {data_filename} does not exist. Creating new file.")
            with open(data_filename, 'w') as f:
                json.dump(data, f, indent=4)
        else:
            print(f"File {data_filename} already exists. Appending new data.")
            with open(data_filename, 'r') as f:
                data_old = json.load(f)

            data_old_complete = list(data_old.keys())[1]  # "Time Series (60min)"
            data_complete = list(data.keys())[1]          # nouvelles données

            # Fusionner toutes les nouvelles données
            for k, v in data[data_complete].items():
                data_old[data_old_complete][k] = v  # ajoute ou remplace

            # Trier les données par date décroissante (Alpha Vantage style)
            sorted_items = sorted(
                data_old[data_old_complete].items(),
                key=lambda x: datetime.strptime(x[0], '%Y-%m-%d %H:%M:%S'),
                reverse=True
            )
            data_old[data_old_complete] = dict(sorted_items)

            # Écrire le fichier fusionné
            with open(data_filename, 'w') as f:
                json.dump(data_old, f, indent=4)

