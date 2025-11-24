from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler
import numpy as np
from analysis.analyzers.data_loader import DataLoader
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.collections import PathCollection
from sklearn.decomposition import PCA
import pickle
from typing import Any

cwd = Path.cwd() # Used in multiple places

dl = DataLoader(ticker='SPY', path_builder=lambda t: cwd/'data'/'SPY'/t/'historical_pct.jsonl')

data = dl.df

window_size = 5
windows_list: list[np.ndarray] = []
for i in range(0, len(data) - window_size + 1, 1):
    window = data.iloc[i:i+window_size].values.flatten()
    windows_list.append(window)
windows: np.ndarray = np.array(windows_list)

windows = StandardScaler().fit_transform(windows)

with open(cwd/'analysis/tokenization/visualizations/gmm_model.pkl', 'rb') as f:
    loaded_gmm: GaussianMixture = pickle.load(f)

cluster_labels = loaded_gmm.predict(windows)
cluster_probs = loaded_gmm.predict_proba(windows)
number_of_clusters: int = loaded_gmm.n_components
# associate each window with a cluster probability distribution:
cluster_annotated_windows = [{ "window": windows[i], "probabilities": cluster_probs[i] } for i in range(len(windows))]

def cluster_entropy(probs: np.ndarray) -> float:
    """Lower entropy = better separation"""
    # Avoid log(0) by adding small epsilon
    eps = 1e-10
    entropy = -np.sum(probs * np.log(probs + eps), axis=1)
    return entropy.mean()


def analyze_cluster_spreads():
    cluster_spreads = []
    for i in range(number_of_clusters):
        if loaded_gmm.covariance_type == 'diag':
            # For diagonal covariance, covariances_[i] is 1D array of variances
            variances = loaded_gmm.covariances_[i]
            cluster_spreads.append(np.sqrt(variances.mean()))
        else:
            # For full covariance, get eigenvalues
            covariances: Any = loaded_gmm.covariances_[i]
            eigenvals = np.linalg.eigvals(covariances)
            cluster_spreads.append(np.sqrt(eigenvals.mean()))

    print("Cluster spreads (standard deviations):")
    for i, spread in enumerate(cluster_spreads):
        print(f"Cluster {i}: {spread:.4f}")

    avg_spread = np.mean(cluster_spreads)
    print(f"Average cluster spread: {avg_spread:.4f}")


def plot_clusters():
    pca = PCA(n_components=2)
    windows_2d = pca.fit_transform(windows)

    plt.figure(figsize=(10, 8))
    scatter = plt.scatter(windows_2d[:, 0], windows_2d[:, 1], c=cluster_labels, cmap='tab10', alpha=0.6)
    plt.colorbar(scatter)
    plt.xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.2%} variance)')
    plt.ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.2%} variance)')
    plt.title(f'GMM Clusters (k={number_of_clusters}) - PCA Projection')
    plt.show()

    # Create scatter plot colored by cluster labels
    plt.figure(figsize=(12, 5))

    # Plot 1: Cluster assignments
    plt.subplot(1, 2, 1)
    scatter: PathCollection = plt.scatter(windows_2d[:, 0], windows_2d[:, 1], c=cluster_labels, cmap='viridis', alpha=0.6)
    plt.colorbar(scatter)
    plt.xlabel('PC1')
    plt.ylabel('PC2')
    plt.title(f'GMM Clustering (k={number_of_clusters})')

    # Plot 2: Cluster probabilities (uncertainty)
    plt.subplot(1, 2, 2)
    max_probs = np.max(cluster_probs, axis=1)
    scatter2 = plt.scatter(windows_2d[:, 0], windows_2d[:, 1], c=max_probs, cmap='coolwarm', alpha=0.6)
    plt.colorbar(scatter2, label='Max Probability')
    plt.xlabel('PC1')
    plt.ylabel('PC2')
    plt.title('Clustering Uncertainty (darker = more certain)')

    plt.tight_layout()
    plt.show()

def view_examples(num_plots: int = 25) -> None:
    # cluster_sizes = np.bincount(cluster_labels)

    cols = int(np.ceil(np.sqrt(num_plots)))
    rows = int(np.ceil(num_plots / cols))

    plt.figure(figsize=(cols * 1.5, rows * 1.5))

    
    for i in range(num_plots):
        plt.subplot(rows, cols, i+1)
        cluster_windows = windows[cluster_labels == i]
        avg_window = cluster_windows.mean(axis=0).reshape(5, 5)

        vmax = np.abs(avg_window).max()
        plt.imshow(avg_window, cmap='RdBu_r', aspect='auto', 
                  vmin=-vmax, vmax=vmax)
        plt.colorbar()
        plt.title(f'C {i} (n={len(cluster_windows)})')
    plt.tight_layout()
    plt.show()

print(cluster_entropy(cluster_probs))
analyze_cluster_spreads()
view_examples(number_of_clusters)

