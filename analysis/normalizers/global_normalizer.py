import pandas as pd
import numpy as np

class GlobalNormalizer:
    def __init__(self, data: np.ndarray) -> None:
        self.data: np.ndarray = data
        self.mean = None
        self.std = None

    def fit(self):
        """Calculate the mean and standard deviation of the data."""
        self.mean = sum(self.data) / len(self.data)
        variance = sum((x - self.mean) ** 2 for x in self.data) / len(self.data)
        self.std = variance ** 0.5

    def normalize(self):
        """Normalize the data using the calculated mean and standard deviation."""
        if self.mean is None or self.std is None:
            raise ValueError("The normalizer must be fitted before normalization.")
        return [(x - self.mean) / self.std for x in self.data]

    def denormalize(self, normalized_data: pd.DataFrame):
        """Denormalize the data back to the original scale."""
        if self.mean is None or self.std is None:
            raise ValueError("The normalizer must be fitted before denormalization.")
        return [x * self.std + self.mean for x in normalized_data]