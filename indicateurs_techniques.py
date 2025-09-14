import polars as pl

def sma(df, period, column='close'):
    return df.select(
        pl.col(column).rolling_mean(window_size=period).alias(f'sma_{period}')
    )

def rsi(df, period=14, column='close'):
    delta = df.select(pl.col(column).diff().alias('delta'))
    gain = delta.select(
        pl.when(pl.col('delta') > 0).then(pl.col('delta')).otherwise(0).alias('gain')
    )
    loss = delta.select(
        pl.when(pl.col('delta') < 0).then(-pl.col('delta')).otherwise(0).alias('loss')
    )

    avg_gain = gain.select(
        pl.col('gain').rolling_mean(window_size=period).alias('avg_gain')
    )
    avg_loss = loss.select(
        pl.col('loss').rolling_mean(window_size=period).alias('avg_loss')
    )
    df_avg = avg_gain.hstack(avg_loss)  # combine les deux colonnes
    rs = df_avg.select((pl.col('avg_gain') / pl.col('avg_loss')).alias('rs'))
    rsi = rs.select(
        (100 - (100 / (1 + pl.col('rs')))).alias(f'rsi_{period}')
    )

    return rsi

def macd(df, short_period=12, long_period=26, signal_period=9, column='close'):
    ema_short = df.select(
        pl.col(column).ewm_mean(alpha=2/(short_period+1)).alias('ema_short')
    )
    ema_long = df.select(
        pl.col(column).ewm_mean(alpha=2/(long_period+1)).alias('ema_long')
    )
    macd_line = ema_short.hstack(ema_long).select(
        (pl.col('ema_short')-pl.col('ema_long')).alias('macd_line')
    )
    signal_line = macd_line.select(
        pl.col('macd_line').ewm_mean(alpha=2/(signal_period+1)).alias('signal_line')
    )
    histogram = macd_line.hstack(signal_line).select(
        (pl.col('macd_line')-pl.col('signal_line')).alias('histogram')
    )
    return macd_line.hstack(signal_line).hstack(histogram)


def bollinger_bands(df, period=20, num_std_dev=2, column='close'):
    sma = df.select(
        pl.col(column).rolling_mean(window_size=period).alias('sma')
    )
    rolling_std = df.select(
        pl.col(column).rolling_std(window_size=period).alias('rolling_std')
    )
    bb = sma.hstack(rolling_std).select(
        (pl.col('sma')+num_std_dev*pl.col('rolling_std')).alias('bb_upper'),
        (pl.col('sma')-num_std_dev*pl.col('rolling_std')).alias('bb_lower')
    )
    return sma.hstack(bb)