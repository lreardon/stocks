import pandas as pd
import random
from typing import Callable
# import math

def test_strategy(df: pd.DataFrame):
    sigma = 0.01
    random_func: Callable[[pd.Series], float] = lambda _: random.lognormvariate(mu=0, sigma=sigma)

    df['profit_ratio'] = df.apply(
        random_func,
        axis=1
    )
    return df