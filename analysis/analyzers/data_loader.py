import pandas as pd
from pathlib import Path
from typing import Callable

class DataLoader:
    ticker: str
    df: pd.DataFrame
    path: Path

    def __init__(self, ticker: str, path_builder: Callable[[str], Path] | None = None) -> None:
        self.ticker = ticker

        _path_builder: Callable[[str], Path] = path_builder or (lambda t: Path.cwd()/'data'/t/'tiingo/historical.jsonl')
        self.path = _path_builder(ticker)

    def load_data_from_path(self, path: Path) -> None:
        lines: bool = path.name.endswith('.jsonl')
        self.df = pd.read_json(str(path), lines=lines)

    def load_historical(self) -> None:                
        self.load_data_from_path(self.path)
