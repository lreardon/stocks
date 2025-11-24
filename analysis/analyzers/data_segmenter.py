from analysis.transformation import Transformation
from analysis.analyzers.data_transformer import DataTransformer
from analysis.segmenters.segmenter import Segmenter
from pathlib import Path
import pandas as pd
import pickle
import numpy as np

class DataSegmenter(DataTransformer):
    segmenter: Segmenter
    segments: list[pd.DataFrame]
    transformation: Transformation
    ticker: str

    def __init__(self,
                 ticker: str,
                 transformation: Transformation,
                 segmenter: Segmenter,
    ) -> None:
        super().__init__(ticker, transformation)
        self.segmenter = segmenter
        # if (self.segments is not None):
            # self.segments: list[pd.DataFrame] | None = None

    
    def use_segmenter(self, segmenter: Segmenter):
        self.segmenter = segmenter
    
    def segment_data(self):
        self.segments = self.segmenter(self.transformed_df)
    
    def save_segmented_data(self):
        cwd = Path.cwd()
        datapath: Path = cwd/'studies'/self.ticker/self.transformation_name/'segmented'/'test'/'data.pkl'
        datapath.parent.mkdir(parents=True, exist_ok=True)
        with open(datapath, 'wb') as f:
            pickle.dump(self.segments, f)

    
    def load_segmented_data(self, path: Path):
        with open(path, 'rb') as f:
            self.segments = pickle.load(f)

    def vectorize_segments(self) -> None:
        self.vectorized_segments: list[np.ndarray] = [segment.values.flatten() for segment in self.segments]