from typing import Protocol
import pandas as pd

class Segmenter(Protocol):
    def __call__(self, df: pd.DataFrame) -> list[pd.DataFrame]:
        ...