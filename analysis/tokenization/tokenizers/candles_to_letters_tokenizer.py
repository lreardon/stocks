from sklearn.mixture import GaussianMixture
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
# from analysis.analyzers.data_loader import DataLoader
import pickle
from pathlib import Path

class CandlesToLettersTokenizer:
    def __init__(self, model: GaussianMixture):
        self.model = model
        self.letters = [chr(i) for i in range(65, 65 + model.n_components)]

    def transform(self, data: pd.DataFrame):
        window_size = 5
        windows = []
        for i in range(0, len(data) - window_size + 1, 1):
            window = data.iloc[i:i+window_size].values.flatten()
            windows.append(window)
        windows = np.array(windows)

        windows = StandardScaler().fit_transform(windows)
        labels = self.model.predict(windows)

        self.transformed_data = [self.letters[label] for label in labels]

    def save_transformed_data(self, filepath: Path):
        with open(filepath, 'w') as f:
            f.write(''.join(self.transformed_data))

cwd = Path.cwd()
with open(cwd/'analysis/tokenization/visualizations/gmm_model.pkl', 'rb') as f:
    model: GaussianMixture = pickle.load(f)

# dl = DataLoader()

# dl.load_data_from_path(cwd/'data'/'SPY'/'tiingo'/'historical_pct.jsonl')
# data = dl.df

# clt = CandlesToLettersTokenizer(model=model)
# clt.transform(data)
# clt.save_transformed_data(cwd/'data'/'SPY'/'analysis'/'historical_pct'/'encoded_sequence.txt')