
import time
from get_data_manager import recuperer_les_datas
from datetime import datetime
print(datetime.now())
import polars as pl
from indicateurs_techniques import sma, rsi, macd, bollinger_bands
import matplotlib.pyplot as plt
#TODO
# [X] Faire fonctionner l'API
# [X] Récupérer les données en JSON
# [X] avoir les données propre
# [X] Sauvegarder les données dans un fichier
# [X] Vérifier si des données manquent ou s'il faut plusieurs appels pour tout récupérer ( 25 call par jour donc risquer, je ne prefere pas)
# [X] transformer le code en def pour pouvoir l'appeler plusieurs fois ( calcul du nombre de mois et demander pour chaque mois)
# [X] Transformer les données en DataFrame
# [X] Coder l'indicateur/ les indicateurs
# [X] l'indicateur renvoie des données et nous on verifie si c'est > ou < a une valeur
# [X] Visualiser l'indicateur et les prix
# [X] Réfléchir à une stratégie de trading
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

# Trier le DataFrame par ordre chronologique
time_series_df = time_series_df.sort("datetime")

#5h par jour donc 25 = 5 jours = 1 semaine
sma50 = sma(time_series_df, 50, 'close')
time_series_df = time_series_df.with_columns(sma50)
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
#
#LA STRATEGIE DE TRADING :
# superieur a la sma + superieur a 65 rsi = on rentre
# inferieur a la sma OU RSI inferieur a 45 on sort
#
# --- Tracé du graphique avec mplfinance ---
import mplfinance as mpf

# 1. Convertir le DataFrame polars en pandas pour mplfinance
df_pandas = time_series_df.to_pandas()

# 2. Définir la colonne 'datetime' comme index (requis par mplfinance)
df_pandas.set_index('datetime', inplace=True)

# 3. Renommer les colonnes pour correspondre aux attentes de mplfinance (majuscule requise)
df_pandas.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
}, inplace=True)

# 4. Préparer les tracés additionnels (indicateurs)
# Les indicateurs qui se superposent au prix (overlays)
overlays = [
    mpf.make_addplot(df_pandas['sma_50'], color='blue', width=0.7),
    mpf.make_addplot(df_pandas['sma'], color='orange', linestyle='--', width=0.7, alpha=0.7), # SMA des bandes de Bollinger
    mpf.make_addplot(df_pandas['bb_upper'], color='gray', alpha=0.5, width=0.7),
    mpf.make_addplot(df_pandas['bb_lower'], color='gray', alpha=0.5, width=0.7)
]

# Les indicateurs dans des panneaux séparés
# Panel 1: RSI
panel1_rsi = mpf.make_addplot(df_pandas['rsi_14'], panel=1, color='purple', ylabel='RSI')

# Panel 2: MACD
panel2_macd_line = mpf.make_addplot(df_pandas['macd_line'], panel=2, color='blue', ylabel='MACD')
panel2_signal_line = mpf.make_addplot(df_pandas['signal_line'], panel=2, color='orange')
# L'histogramme en barres
colors = ['green' if val >= 0 else 'red' for val in df_pandas['histogram']]
panel2_histogram = mpf.make_addplot(df_pandas['histogram'], type='bar', panel=2, color=colors, alpha=0.7)


# Rassembler tous les tracés additionnels
addplots = overlays + [panel1_rsi, panel2_macd_line, panel2_signal_line, panel2_histogram]

# 5. Tracer le graphique final
mpf.plot(df_pandas,
         type='candle',  # Type de graphique: 'candle', 'line', 'ohlc'
         style='yahoo',  # Style visuel
         title=f'Analyse Technique de {SYMBOL}',
         ylabel='Prix ($)',
         addplot=addplots,
         panel_ratios=(6, 2, 3),  # Ratio de taille pour (graphique principal, panel 1, panel 2)
         figscale=1.5,           # Agrandir la figure globale
         volume=True,            # Afficher le volume dans son propre panneau
         figsize=(15, 10)
        )