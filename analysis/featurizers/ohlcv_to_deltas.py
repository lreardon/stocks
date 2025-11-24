import pandas as pd

def ohlcv_to_deltas(df: pd.DataFrame):
    wdf = df.copy()

    wdf['open_delta'] = wdf['open'] / wdf['open'].shift(1) - 1
    wdf['high_delta'] = wdf['high'] / wdf['high'].shift(1) - 1
    wdf['low_delta'] = wdf['low'] / wdf['low'].shift(1) - 1
    wdf['close_delta'] = wdf['close'] / wdf['close'].shift(1) - 1
    wdf.dropna(inplace=True)

    rdf = wdf['open_delta high_delta low_delta close_delta volume'.split()]
    return rdf