import pandas as pd
from ta.momentum import StochasticOscillator
from ta.volatility import AverageTrueRange
from ta.volume import VolumeWeightedAveragePrice

def scalp2(df: pd.DataFrame,
            vwap_param: int = 14,
            stoch_param: int = 5,
            stoch_smooth_param: int = 3,
            atr_param: int = 20,
            volume_ema_param: int = 20,
    ):

    wdf = df.copy()

    wdf['vwap'] = VolumeWeightedAveragePrice(
        high=wdf['high'],
        low=wdf['low'],
        close=wdf['close'],
        volume=wdf['volume'],
        window=vwap_param
    ).volume_weighted_average_price()

    wdf['volume_ema'] = wdf['volume'].ewm(span=volume_ema_param, adjust=False).mean()

    wdf['stoch'] = StochasticOscillator(
        high=wdf['high'],
        low=wdf['low'],
        close=wdf['close'],
        window=stoch_param,
        smooth_window=stoch_smooth_param,
    ).stoch()

    wdf['volume_delta'] = wdf['volume'] - wdf['volume'].shift(1)

    wdf['atr'] = AverageTrueRange(
        high=wdf['high'],
        low=wdf['low'],
        close=wdf['close'],
        window=atr_param,
    ).average_true_range()


    wdf.dropna(inplace=True)

    rdf = wdf['vwap stoch volume_delta atr'.split()]
    return rdf