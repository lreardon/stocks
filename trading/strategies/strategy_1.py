import pandas as pd

def strategy_1(df: pd.DataFrame):

    trade_duration = 10

    returns = []
    
    for i in range(len(df)):
        # Ensure enough data at end of data.
        if i + trade_duration >= len(df):
            returns.append(1)
            continue
            
        # Do not trade at end of day.
        current_date: pd.Timestamp = df.iloc[i]['date']
        terminal_date: pd.Timestamp = df.iloc[i+trade_duration]['date']
        if (current_date.weekday() != terminal_date.weekday()):
            returns.append(1)
            continue

        buy_price = df.iloc[i]['open']

        score = None
        j = 0
        
        while score is None:
            if df.iloc[i+j]['high'] > buy_price * 1.01:
                score =  1.01
            if df.iloc[i+j]['low'] < buy_price * 0.98:
                score = 0.98
            j += 1
            if j >= trade_duration:
                score = df.iloc[i+trade_duration]['close'] / buy_price
        
        returns.append(score)

    df['profit_ratio'] = returns

    return df