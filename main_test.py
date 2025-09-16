import time
from get_data_manager import recuperer_les_datas
from datetime import datetime
import polars as pl
from indicateurs_techniques import sma, rsi

# --- Import des nouveaux modules ---
from backtester_test import vectorized_backtest
from plotting_test import plot_best_strategy

print(f"Début du script : {datetime.now()}")

# --- PARAMÈTRES DE CONFIGURATION ---
# Paramètres de données
SYMBOL = 'AAPL'
INTERVAL = '60min'
DATE_DEBUT = '2008-12'
DATE_FIN = '2009-12'

# Paramètres de la stratégie (plus de nombres magiques !)
RSI_BUY_THRESHOLD = 65
RSI_SELL_THRESHOLD = 45
INITIAL_PORTFOLIO = 10000

# Paramètres à tester
LIST_SMA_PERIODS = [50, 100, 150, 200]
LIST_RSI_PERIODS = [10, 14, 15, 20, 21]


# --- 1. CHARGEMENT ET PRÉPARATION DES DONNÉES ---
recuperer_les_datas(DATE_DEBUT, DATE_FIN, 'TIME_SERIES_INTRADAY', SYMBOL, INTERVAL, 'false', 'false', 'full', 'json')

df = pl.read_json(f"{SYMBOL}{INTERVAL}.json")
time_series_dict = df["Time Series (60min)"][0]
time_series_df = pl.DataFrame({
    "datetime": list(time_series_dict.keys()),
    "open": [float(v["1. open"]) for v in time_series_dict.values()],
    "high": [float(v["2. high"]) for v in time_series_dict.values()],
    "low": [float(v["3. low"]) for v in time_series_dict.values()],
    "close": [float(v["4. close"]) for v in time_series_dict.values()],
    "volume": [int(v["5. volume"]) for v in time_series_dict.values()],
}).with_columns(
    pl.col("datetime").str.strptime(pl.Datetime, "%Y-%m-%d %H:%M:%S")
).sort("datetime")


# --- 2. CALCUL DES INDICATEURS ET SIGNAUX ---
print("Calcul des indicateurs et génération des signaux...")
for sma_period in LIST_SMA_PERIODS:
    time_series_df = time_series_df.with_columns(sma(time_series_df, sma_period, 'close'))
for rsi_period in LIST_RSI_PERIODS:
    time_series_df = time_series_df.with_columns(rsi(time_series_df, rsi_period, 'close'))

for sma_period in LIST_SMA_PERIODS:
    for rsi_period in LIST_RSI_PERIODS:
        sma_col = f'sma_{sma_period}'
        rsi_col = f'rsi_{rsi_period}'
        signal_col_name = f'signal_{sma_period}_{rsi_period}'
        
        time_series_df = time_series_df.with_columns(
            pl.when((pl.col("close") > pl.col(sma_col)) & (pl.col(rsi_col) > RSI_BUY_THRESHOLD))
            .then(pl.lit("Achat"))
            .when((pl.col("close") < pl.col(sma_col)) | (pl.col(rsi_col) < RSI_SELL_THRESHOLD))
            .then(pl.lit("Vente"))
            .otherwise(None)
            .alias(signal_col_name)
        )
print("Tous les signaux ont été générés.")


# --- 3. EXÉCUTION DU BACKTESTING ---
print("Exécution du backtest vectorisé...")
start_time = time.time()
list_PNL = []
for sma_period in LIST_SMA_PERIODS:
    for rsi_period in LIST_RSI_PERIODS:
        signal_col_to_test = f'signal_{sma_period}_{rsi_period}'
        # Appel de la nouvelle fonction vectorisée
        result = vectorized_backtest(time_series_df, signal_col_name=signal_col_to_test, initial_portfolio=INITIAL_PORTFOLIO)
        list_PNL.append((result, "SMA", sma_period, "RSI", rsi_period))
end_time = time.time()
print(f"Backtest terminé en {end_time - start_time:.2f} secondes.")


# --- 4. ANALYSE DES RÉSULTATS ET AFFICHAGE ---
list_PNL.sort(reverse=True)
print("\n--- Meilleurs résultats du backtest ---")
for resultat in list_PNL[:5]:
    print(resultat)

# Extraire les meilleurs paramètres
best_result = list_PNL[0]
best_sma_period = best_result[2]
best_rsi_period = best_result[4]
best_sma_col = f'sma_{best_sma_period}'
best_rsi_col = f'rsi_{best_rsi_period}'

# Appel de la nouvelle fonction de plotting
plot_best_strategy(
    df=time_series_df,
    best_sma_col=best_sma_col,
    best_rsi_col=best_rsi_col,
    symbol=SYMBOL,
    rsi_buy_threshold=RSI_BUY_THRESHOLD,
    rsi_sell_threshold=RSI_SELL_THRESHOLD
)