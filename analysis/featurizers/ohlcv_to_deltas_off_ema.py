import pandas as pd

def ohlcv_to_deltas_off_ema(df: pd.DataFrame, *, ema_span: int):
    wdf = df.copy()
    # wdf['cash_volume'] = (wdf['open'] + wdf['close']) / 2 * wdf['volume']
    
    wdf['open_ema'] = wdf['open'].ewm(span=ema_span, adjust=False).mean()
    wdf['high_ema'] = wdf['high'].ewm(span=ema_span, adjust=False).mean()
    wdf['low_ema'] = wdf['low'].ewm(span=ema_span, adjust=False).mean()
    wdf['close_ema'] = wdf['close'].ewm(span=ema_span, adjust=False).mean()
    # wdf['cash_volume_ema'] = wdf['cash_volume'].ewm(span=ema_span, adjust=False).mean()


    wdf['open_delta'] = wdf['open'] / wdf['open_ema'].shift(1) - 1
    wdf['high_delta'] = wdf['high'] / wdf['high_ema'].shift(1) - 1
    wdf['low_delta'] = wdf['low'] / wdf['low_ema'].shift(1) - 1
    wdf['close_delta'] = wdf['close'] / wdf['close_ema'].shift(1) - 1
    # wdf['cash_volume_delta'] = wdf['cash_volume'] / wdf['cash_volume_ema'].shift(1) - 1
    wdf.dropna(inplace=True)

    rdf = wdf['open_delta high_delta low_delta close_delta volume'.split()]
    return rdf