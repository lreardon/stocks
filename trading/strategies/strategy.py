import pandas as pd
from typing import Protocol

class Strategy(Protocol):
    def __call__(self, df: pd.DataFrame, name: str) -> pd.DataFrame:
        ...