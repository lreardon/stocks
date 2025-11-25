from pathlib import Path
import pandas as pd
from pandas import DataFrame
from typing import Callable, TypedDict

class InputOutput(TypedDict):
    input: DataFrame
    output: DataFrame

class DataPipeline(TypedDict):
    raw: DataFrame
    segmented: list[DataFrame]
    labeled: list[InputOutput]


class MultiTickerDataLoader:
    tickers: list[str]
    data: dict[str, DataPipeline]
    path_builder: Callable[[str], Path]
    
    def __init__(
        self,
        tickers: list[str],
        path_builder: Callable[[str], Path] | None = None,
    ) -> None:
        self.data = {}
        self.tickers = tickers
        self.path_builder: Callable[[str], Path] = path_builder or (lambda t: Path.cwd()/'data'/t/'tiingo/historical.jsonl')

    def load(self) -> None:
        for ticker in self.tickers:
            if ticker not in self.data:
                self.data[ticker] = DataPipeline(
                    raw=DataFrame(),
                    segmented=[],
                    labeled=[],
                )
            
            ticker_path: Path = self.path_builder(ticker)
            lines: bool = ticker_path.name.endswith('.jsonl')
            self.data[ticker]['raw'] = pd.read_json(
                str(ticker_path),
                lines=lines
            )
    
    def build_windows(
        self,
        window_builder: Callable[[DataFrame], list[DataFrame]]
    ) -> None:
        for ticker in self.tickers:
            raw_data: DataFrame = self.data[ticker]['raw']
            windows: list[DataFrame] = window_builder(raw_data)
            self.data[ticker]['segmented'] = windows
    
    def build_inputs_outputs(
        self,
        io_builder: Callable[[list[DataFrame]], list[InputOutput]]
    ) -> None:
        for ticker in self.tickers:
            segmented_data: list[DataFrame] = self.data[ticker]['segmented']
            labeled_data: list[InputOutput] = io_builder(segmented_data)
            self.data[ticker]['labeled'] = labeled_data