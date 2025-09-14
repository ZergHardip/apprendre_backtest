
from get_data_manager import recuperer_les_datas
from datetime import datetime
print(datetime.now())

#TODO
# [X] Faire fonctionner l'API
# [X] Récupérer les données en JSON
# [X] avoir les données propre
# [X] Sauvegarder les données dans un fichier
# [X] Vérifier si des données manquent ou s'il faut plusieurs appels pour tout récupérer ( 25 call par jour donc risquer, je ne prefere pas)
# [X] transformer le code en def pour pouvoir l'appeler plusieurs fois ( calcul du nombre de mois et demander pour chaque mois)
# [] Transformer les données en DataFrame
# [] Coder l'indicateur
# [] Réfléchir à une stratégie de trading
# [] Visualiser l'indicateur et les prix
# [] Faire le backtest de la stratégie
# [] Faire un for pour tester plusieurs paramètres
# [] Faire l'optimisation des paramètres

FUNCTION = 'TIME_SERIES_INTRADAY'
SYMBOL = 'AAPL'
INTERVAL = '60min'
ADJUSTED = 'false'
EXTENDED_HOURS = 'false'
MONTH = '2009-06'
OUTPUTSIZE = 'full'
DATATYPE = 'json'
"""VERIFICATOIN DE L'API
import requests
import json
from datetime import date, timedelta, datetime
from os import path
from api_config import API_KEY, BASE_URL
url = BASE_URL + "function=" + FUNCTION + "&symbol="+SYMBOL+"&interval="+INTERVAL+"&adjusted="+ADJUSTED+"&extended_hours="+EXTENDED_HOURS+"&month="+MONTH+"&outputsize="+OUTPUTSIZE+"&datatype="+DATATYPE+"&apikey=" + API_KEY
r = requests.get(url)
data = r.json()
print(data)"""
#attention a ne pas faire trop d'appel a l'api, 25/jour

recuperer_les_datas('2008-12','2009-12',FUNCTION, SYMBOL, INTERVAL, ADJUSTED, EXTENDED_HOURS, OUTPUTSIZE, DATATYPE)


