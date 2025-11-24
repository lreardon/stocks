import pandas as pd
from typing import Protocol

class Transformation(Protocol):

    def __call__(self, df: pd.DataFrame) -> pd.DataFrame:
        ...