from analysis.analyzers.data_loader import DataLoader
from analysis.transformation import Transformation
from pathlib import Path
import pandas as pd

class DataTransformer(DataLoader):
    transformation: Transformation
    transformed_df: pd.DataFrame
    transformation_name: str

    def __init__(self, ticker: str, transformation: Transformation, transformation_name: str | None = None) -> None:
        super().__init__(ticker)
        self.transformation: Transformation = transformation
        self.transformation_name = transformation_name or transformation.__class__.__name__

    def transform_data(self) -> None:
        self.transformed_df: pd.DataFrame = self.transformation(self.df)
    
    def save_transformed_data(self) -> None:
        cwd = Path.cwd()
        datapath: Path = cwd/'studies'/self.ticker/self.transformation_name/'data.jsonl'
        datapath.parent.mkdir(parents=True, exist_ok=True)
        with open(datapath, 'w') as f:
            f.write(self.transformed_df.to_json(orient='records', lines=True))
