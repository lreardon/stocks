# from curses import window
import pandas as pd
from ta.momentum import RSIIndicator
from ta.volume import VolumeWeightedAveragePrice
from trading.strategies.enums.exit_type import ExitType
from typing import Callable

def strategy_2(df: pd.DataFrame):

    trade_duration = 60
    rsi_param = 14
    rsi_oversold_threshold = 30
    vwap_param = 10
    constant_take_profit_ratio = 1.005
    constant_stop_loss_ratio = 0.99

    # RSI ranges from 0 to 100
    df['rsi'] = RSIIndicator(df['close'], window=rsi_param).rsi()
    df['vwap'] = VolumeWeightedAveragePrice(
        high=df['high'],
        low=df['low'],
        close=df['close'],
        volume=df['volume'],
        window=vwap_param,
    ).volume_weighted_average_price()

    df['vwap_extension'] = (df['close'] - df['vwap']) / df['close']

    returns = []
    exit_types = []

    # Implement returns and metadata logic for no trade.
    def no_trade():
        returns.append(1)
        exit_types.append('')


    for i in range(len(df)):
        # if i % 5000 == 0:
        #     print(i)

        # Ensure enough data at end of data.
        if i + trade_duration >= len(df):
            no_trade()
            continue
            
        # Do not trade at end of day.
        current_datetime: pd.Timestamp = df.iloc[i]['date']
        terminal_datetime: pd.Timestamp = df.iloc[i+trade_duration]['date']
        if (current_datetime.weekday() != terminal_datetime.weekday()):
            no_trade()
            continue

        # Do not trade if rsi and vwap are not computed within same day.
        max_lookback_param = max([rsi_param, vwap_param])
        lookback_window_first_candle_datetime: pd.Timestamp  = df.iloc[i-max_lookback_param]['date']
        if (lookback_window_first_candle_datetime.weekday() != current_datetime.weekday()):
            no_trade()
            continue

        # Only enter if rsi is known
        if pd.isna(df.iloc[i]['rsi']):
            no_trade()
            continue

        # Only enter if vwap_extension is known
        if pd.isna(df.iloc[i]['vwap_extension']):
            no_trade()
            continue
    
        
        # Enter only if last 3 rsi exist...
        if not (i >= 3 and df.iloc[i-3]['rsi'] != None):
            no_trade()
            continue

        # ... and were oversold....
        oversold_indicator: Callable[[float], bool] = lambda e: e < rsi_oversold_threshold

        if not df.iloc[i-3:i]['rsi'].apply(oversold_indicator).all():
            no_trade()
            continue

        # ... but we are currently not oversold!
        if not df.iloc[i]['rsi'] > rsi_oversold_threshold:
            no_trade()
            continue

        # Enter only if vwap is extending negatively.
        if not df.iloc[i]['vwap_extension'] < 0.99:
            no_trade()
            continue

        # Enter trade.
        buy_price = df.iloc[i+1]['open']
        score = None
        exit_type = None
        j = 0
        while score is None and exit_type is None:
            j += 1
            take_profit_ratio = constant_take_profit_ratio
            stop_loss_ratio = constant_stop_loss_ratio

            if df.iloc[i+j]['high'] > buy_price * take_profit_ratio:
                score = take_profit_ratio
                exit_type = ExitType.TAKE_PROFIT
                continue

            if df.iloc[i+j]['low'] < buy_price * stop_loss_ratio:
                score = stop_loss_ratio
                exit_type = ExitType.STOP_LOSS
                continue

            if j >= trade_duration:
                score = df.iloc[i+trade_duration]['close'] / buy_price
                exit_type = ExitType.TIMEOUT
                continue

        returns.append(score)
        exit_types.append(exit_type)


    df['profit_ratio'] = returns
    df['exit_type'] = exit_types

    return df