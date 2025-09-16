import time
from turtle import back
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
# [X] Faire le backtest de la stratégie
# [X] Faire un for pour tester plusieurs paramètres
# [X] Faire l'optimisation des paramètres

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

# --- Backtesting Loop ---
PORTFOLIO = 10000
CASH = PORTFOLIO
SHARES = 0

list_des_sma = [50,100,150,200]
liste_des_rsi = [10,14,15,20,21]

for sma_period in list_des_sma:
    sma_indicator = sma(time_series_df, sma_period, 'close')
    time_series_df = time_series_df.with_columns(sma_indicator)
for rsi_period in liste_des_rsi:
    rsi_indicator = rsi(time_series_df, rsi_period, 'close')
    time_series_df = time_series_df.with_columns(rsi_indicator)
#print(time_series_df)


#
#LA STRATEGIE DE TRADING :
# superieur a la sma + superieur a 65 rsi = on rentre
# inferieur a la sma OU RSI inferieur a 45 on sort
#
def backtest(time_series_df, sma, rsi, portfolio=10000, cash=10000, shares=0):
    

    time_series_df = time_series_df.with_columns(
        pl.when((pl.col("close") > pl.col(str(sma))) & (pl.col(str(rsi)) > 65))
        .then(pl.lit("Achat"))
        .when((pl.col("close") < pl.col(str(sma))) | (pl.col(str(rsi)) < 45))
        .then(pl.lit("Vente"))
        .otherwise(None) # Mettre None pour les signaux neutres
        .alias("signal")
    )

    in_position = False
    buy_signals = []
    sell_signals = []
    for row in time_series_df.iter_rows(named=True):
        signal = row['signal']
        close_price = row['close']
        current_date = row['datetime']

        if signal == "Achat" and not in_position:
            shares_to_buy = cash // close_price
            if shares_to_buy > 0:
                shares = shares_to_buy
                cash -= shares * close_price
                in_position = True
                #print(f"Achat de {shares} actions le {current_date} à {close_price:.2f}$")

        elif signal == "Vente" and in_position:
            cash += shares * close_price
            shares = 0
            in_position = False
            #print(f"Vente de toutes les actions le {current_date} à {close_price:.2f}$")

    portefeuille_final = cash + shares * time_series_df.item(-1, 'close')
    #print(f"Portefeuille initial : {portfolio:.2f} $")
    #print(f"Portefeuille final : {portefeuille_final:.2f} $")
    performance = (portefeuille_final - portfolio) / portfolio * 100 
    #print(f"Performance : {performance:.2f} %")
    performance_arrondi = round(performance, 2)
    return performance_arrondi
list_PNL = []
for sma_period in list_des_sma:
        for rsi_period in liste_des_rsi:
            sma_col = f'sma_{sma_period}'
            rsi_col = f'rsi_{rsi_period}'
            result = backtest(time_series_df, sma=sma_col, rsi=rsi_col)
            list_PNL.append((result,"SMA", sma_period,"RSI", rsi_period))
list_PNL.sort(reverse=True)
for resultat in list_PNL:
    print(resultat)

# --- Préparation du graphique avec la MEILLEURE stratégie ---

# 1. Extraire les meilleurs paramètres de la liste triée
best_result = list_PNL[0]
best_sma_period = best_result[2]
best_rsi_period = best_result[4]
best_sma_col = f'sma_{best_sma_period}'
best_rsi_col = f'rsi_{best_rsi_period}'

print(f"\n--- Affichage du graphique pour la meilleure stratégie : SMA={best_sma_period}, RSI={best_rsi_period} ---")


# Convertir en pandas pour une mise à jour plus facile de l'index
df_pandas = time_series_df.to_pandas().set_index('datetime')

# --- Tracé du graphique avec mplfinance ---
import mplfinance as mpf

# 3. Renommer les colonnes pour correspondre aux attentes de mplfinance (majuscule requise)
df_pandas.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
}, inplace=True)

# 4. Préparer les tracés additionnels en utilisant les MEILLEURS paramètres
overlays = [
    # Utilise la colonne de la meilleure SMA
    mpf.make_addplot(df_pandas[best_sma_col], color='blue', width=0.7)
]

# Panel 2: Utilise la colonne du meilleur RSI
panel1_rsi = mpf.make_addplot(df_pandas[best_rsi_col], panel=2, color='purple', ylabel='RSI')

# Ajouter les lignes de seuil pour le RSI
rsi_overbought = mpf.make_addplot([65] * len(df_pandas), panel=2, color='orange', linestyle='--')
rsi_oversold = mpf.make_addplot([45] * len(df_pandas), panel=2, color='orange', linestyle='--')

# Rassembler tous les tracés additionnels
addplots = overlays + [panel1_rsi, rsi_overbought, rsi_oversold]

# 5. Tracer le graphique final avec un titre dynamique
mpf.plot(df_pandas,
         type='candle',
         style='yahoo',
         title=f'Stratégie {SYMBOL} - Meilleur Résultat : SMA({best_sma_period}) & RSI({best_rsi_period})',
         ylabel='Prix ($)',
         addplot=addplots,
         panel_ratios=(8, 2, 3),  # Ratio pour (graphique principal, volume, panel RSI)
         figscale=1.5,
         volume=True,
         figsize=(16, 9)
        )