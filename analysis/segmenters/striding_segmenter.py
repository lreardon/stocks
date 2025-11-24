import pandas as pd

def striding_segmenter_builder(
    length: int = 10,
    stride: int = 8,
):
    def _segmenter(df: pd.DataFrame) -> list[pd.DataFrame]:
        segments = []
        j = 0
        while j + length <= len(df):
            segments.append(df.iloc[j:j + length])
            j += stride
        return segments

    return _segmenter