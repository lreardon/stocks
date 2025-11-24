import numpy as np
import pandas as pd
from typing import Callable

def cusum_segmenter(
        df: pd.DataFrame,
        cusum_on: Callable[[pd.DataFrame], pd.Series] = lambda x: x['close'],
        threshold=2.0
    ):
    data: pd.Series = cusum_on(df)
    """CUSUM test for change points"""
    returns = np.diff(np.log(data))
    mean_return = np.mean(returns)
    
    cusum = np.cumsum(returns - mean_return)
    boundaries = []
    
    for i in range(len(cusum)):
        if abs(cusum[i]) > threshold * np.std(returns):
            boundaries.append(i)
            cusum = cusum - cusum[i]  # Reset
    
    segments = np.split(df, boundaries)
    return segments