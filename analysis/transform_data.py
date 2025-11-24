from analysis.analyzers.data_transformer import DataTransformer
from analysis.featurizers.ohlcv_to_deltas_off_ema import ohlcv_to_deltas_off_ema
import pandas as pd

def ohlcv_to_deltas_off_ema_20(df: pd.DataFrame) -> pd.DataFrame:
    return ohlcv_to_deltas_off_ema(df, ema_span=20)

dt = DataTransformer(
    ticker='SPY',
    transformation = ohlcv_to_deltas_off_ema_20,    
    transformation_name='ohlcv_to_deltas_off_ema_20'
)

dt.load_historical()

dt.transform_data()

print(dt.transformed_df)

dt.save_transformed_data()
