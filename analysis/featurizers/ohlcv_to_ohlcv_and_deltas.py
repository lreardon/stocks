import pandas as pd
# from analysis.transformation import Transformation

def ohlcv_to_ohlcv_and_deltas(df: pd.DataFrame) -> pd.DataFrame:
    wdf = df.copy()

    wdf['open_delta'] = wdf['open'] / wdf['open'].shift(1) - 1
    wdf['high_delta'] = wdf['high'] / wdf['high'].shift(1) - 1
    wdf['low_delta'] = wdf['low'] / wdf['low'].shift(1) - 1
    wdf['close_delta'] = wdf['close'] / wdf['close'].shift(1) - 1
    # wdf['volume_delta'] = wdf['volume'] / wdf['volume'].shift(1) - 1
    wdf.dropna(inplace=True)

    rdf = wdf[['open', 'high', 'low', 'close', 'volume', 'open_delta', 'high_delta', 'low_delta', 'close_delta']]

    return rdf