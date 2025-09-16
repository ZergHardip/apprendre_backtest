import polars as pl

def vectorized_backtest(df: pl.DataFrame, signal_col_name: str, initial_portfolio=10000):
    """
    Exécute un backtest vectorisé sans boucle for sur le DataFrame principal.
    C'est beaucoup plus rapide qu'une approche itérative.
    """
    
    # 1. Identifier les points de transaction exacts en utilisant shift()
    # Un "vrai" signal d'achat : le signal passe à "Achat" et n'était pas "Achat" juste avant.
    buy_triggers = (pl.col(signal_col_name) == "Achat") & (pl.col(signal_col_name).shift(1) != "Achat")
    
    # Un "vrai" signal de vente : le signal passe à "Vente" et on était en position ("Achat").
    sell_triggers = (pl.col(signal_col_name) == "Vente") & (pl.col(signal_col_name).shift(1) == "Achat")

    # 2. Créer un DataFrame contenant uniquement les transactions
    trades_df = df.with_columns(
        pl.when(buy_triggers).then(pl.lit("buy"))
          .when(sell_triggers).then(pl.lit("sell"))
          .otherwise(None)
          .alias("trade_type")
    ).filter(pl.col("trade_type").is_not_null())

    # 3. Simuler le portefeuille en itérant sur le (petit) DataFrame des transactions
    cash = initial_portfolio
    shares = 0
    in_position = False

    # Cette boucle est très rapide car elle ne tourne que sur quelques transactions
    for trade in trades_df.iter_rows(named=True):
        trade_type = trade['trade_type']
        price = trade['close']

        if trade_type == 'buy' and not in_position:
            shares_to_buy = cash // price
            if shares_to_buy > 0:
                shares = shares_to_buy
                cash -= shares * price
                in_position = True
        
        elif trade_type == 'sell' and in_position:
            cash += shares * price
            shares = 0
            in_position = False

    # 4. Calculer la valeur finale du portefeuille
    if in_position:
        final_portfolio_value = cash + shares * df.item(-1, 'close')
    else:
        final_portfolio_value = cash
        
    performance = (final_portfolio_value - initial_portfolio) / initial_portfolio * 100
    return round(performance, 2)