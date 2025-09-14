
import time
from get_data_manager import recuperer_les_datas
from datetime import datetime
print(datetime.now())
import polars as pl
from indicateurs_techniques import sma, rsi, macd, bollinger_bands
#TODO
# [X] Faire fonctionner l'API
# [X] Récupérer les données en JSON
# [X] avoir les données propre
# [X] Sauvegarder les données dans un fichier
# [X] Vérifier si des données manquent ou s'il faut plusieurs appels pour tout récupérer ( 25 call par jour donc risquer, je ne prefere pas)
# [X] transformer le code en def pour pouvoir l'appeler plusieurs fois ( calcul du nombre de mois et demander pour chaque mois)
# [X] Transformer les données en DataFrame
# [X] Coder l'indicateur/ les indicateurs
# [] l'indicateur ne renvoie pas un true false sur les datas ( 12h00 true, 13h00 false, 14h00 true etc...), mais juste un true or false pour que je puisse combine plusieur indicateur ensemble
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


recuperer_les_datas('2008-12','2009-12',FUNCTION, SYMBOL, INTERVAL, ADJUSTED, EXTENDED_HOURS, OUTPUTSIZE, DATATYPE)


# Lire le fichier complet
df = pl.read_json(f"{SYMBOL}{INTERVAL}.json")

# Extraire la colonne "Time Series (60min)" (c'est un dictionnaire)
time_series_dict = df["Time Series (60min)"][0]  # [0] car il n'y a qu'une seule ligne

# Transformer le dictionnaire en DataFrame
time_series_df = pl.DataFrame(
    {
        "datetime": list(time_series_dict.keys()),
        "open": [float(v["1. open"]) for v in time_series_dict.values()],
        "high": [float(v["2. high"]) for v in time_series_dict.values()],
        "low": [float(v["3. low"]) for v in time_series_dict.values()],
        "close": [float(v["4. close"]) for v in time_series_dict.values()],
        "volume": [int(v["5. volume"]) for v in time_series_dict.values()],
    }
)

# Convertir la colonne datetime en vrai type datetime
time_series_df = time_series_df.with_columns(
    pl.col("datetime").str.strptime(pl.Datetime, "%Y-%m-%d %H:%M:%S")
)

sma20 = sma(time_series_df, 20, 'close')
time_series_df = time_series_df.with_columns(sma20)
print(time_series_df)

rsi14 = rsi(time_series_df, 14, 'close')
time_series_df = time_series_df.with_columns(rsi14)
print(time_series_df)

macd_df = macd(time_series_df, 12, 26, 9, 'close')
time_series_df = time_series_df.with_columns(macd_df)
print(time_series_df)

bb_df = bollinger_bands(time_series_df,20,2,'close')
time_series_df = time_series_df.with_columns(bb_df)
print(time_series_df)

