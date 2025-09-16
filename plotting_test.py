import polars as pl
import mplfinance as mpf
import matplotlib.ticker as mticker
import matplotlib.pyplot as plt

def plot_best_strategy(df: pl.DataFrame, best_sma_col: str, best_rsi_col: str, symbol: str, rsi_buy_threshold: int, rsi_sell_threshold: int):
    """
    Affiche le graphique de la meilleure stratégie en utilisant mplfinance.
    """
    print(f"\n--- Affichage du graphique pour la meilleure stratégie : {best_sma_col} & {best_rsi_col} ---")

    # Convertir en pandas pour mplfinance
    df_pandas = df.to_pandas().set_index('datetime')

    # Renommer les colonnes
    df_pandas.rename(columns={
        'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume'
    }, inplace=True)

    # Préparer les tracés additionnels
    addplots = [
        mpf.make_addplot(df_pandas[best_sma_col], color='blue', width=0.7),
        mpf.make_addplot(df_pandas[best_rsi_col], panel=2, color='purple', ylabel='RSI'),
        mpf.make_addplot([rsi_buy_threshold] * len(df_pandas), panel=2, color='orange', linestyle='--'),
        mpf.make_addplot([rsi_sell_threshold] * len(df_pandas), panel=2, color='orange', linestyle='--')
    ]

    # Tracer le graphique et récupérer les objets figure/axes
    fig, axes = mpf.plot(df_pandas,
                         type='candle',
                         style='yahoo',
                         title=f'Stratégie {symbol} - {best_sma_col} & {best_rsi_col}',
                         ylabel='Prix ($)',
                         addplot=addplots,
                         panel_ratios=(8, 2, 3),
                         figscale=1.5,
                         volume=True,
                         figsize=(16, 9),
                         returnfig=True)

    # Personnaliser l'axe du volume pour afficher en Millions
    formatter = mticker.FuncFormatter(lambda y, _: f'{y / 1_000_000:.1f}M')
    axes[1].yaxis.set_major_formatter(formatter)

    # Afficher le graphique
    plt.show()