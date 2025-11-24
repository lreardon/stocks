# from matplotlib.figure import Figure
from matplotlib.pylab import dtype
# from numpy._typing._array_like import NDArray
from pyparsing import Any
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler
import numpy as np
# from analysis.analyzers.data_loader import DataLoader
# from pathlib import Path
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
# import pandas as pd
from sklearn.neighbors import NearestNeighbors
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN
from sklearn.metrics import silhouette_score


class GaussianMixtureCategorizer:
    labels: np.ndarray[tuple[Any, ...], np.dtype[np.Any]]
    gmm: GaussianMixture

    def __init__(self, data: np.ndarray | None = None):
        self.data = data

    def gaussian_mixtures(self) -> np.ndarray[tuple[Any, ...], np.dtype[np.Any]]:
        # Assuming self.data is a 2D array-like structure
        scaled_data: np.ndarray = StandardScaler().fit_transform(self.data)
        gmm = GaussianMixture(n_components=10, covariance_type='full', random_state=42)
        self.labels = gmm.fit_predict(scaled_data)
        self.gmm: GaussianMixture = gmm
        return self.labels
    
    def categorize(self) -> np.ndarray[tuple[Any, ...], np.dtype[np.Any]]:
        scaled_data: np.ndarray = StandardScaler().fit_transform(self.data)
        
        # DBSCAN automatically finds number of clusters
        clustering = DBSCAN(eps=0.5, min_samples=5)
        self.labels = clustering.fit_predict(scaled_data)
        
        return self.labels
    


    def find_optimal_eps(self, data: np.ndarray, min_samples: int = 5) -> np.ndarray:
        """Find optimal eps using k-distance graph"""
        neighbors = NearestNeighbors(n_neighbors=min_samples)
        neighbors_fit: NearestNeighbors = neighbors.fit(data)
        distances, _indices = neighbors_fit.kneighbors(data)
        
        # Sort distances to min_samples-th nearest neighbor
        distances = np.sort(distances[:, min_samples-1], axis=0)
        
        # Plot to find elbow (optimal eps)
        plt.figure(figsize=(8, 4))
        plt.plot(distances)
        plt.xlabel('Points sorted by distance')
        plt.ylabel(f'{min_samples}-NN distance')
        plt.title('K-distance Graph for Optimal Eps')
        plt.show()
        
        # Return suggested eps (where curve has steepest slope)
        return distances

    def categorize_large_dataset(self) -> np.ndarray[tuple[Any, ...], dtype[Any]]:
        from sklearn.cluster import KMeans
        from sklearn.metrics import silhouette_score
        import numpy as np
        
        scaled_data: np.ndarray = StandardScaler().fit_transform(self.data)
        
        # Sample for parameter tuning (use 5000 points)
        n_sample: int = min(5000, len(scaled_data))
        sample_idx = np.random.choice(len(scaled_data), n_sample, replace=False)
        sample_data = scaled_data[sample_idx]
        
        # Find optimal clusters on sample
        best_k = 2
        best_score = -1
        
        for k in range(2, 15):
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            sample_labels = kmeans.fit_predict(sample_data)
            score = silhouette_score(sample_data, sample_labels)
            
            if score > best_score:
                best_score = score
                best_k = k
        
        # Apply optimal k to full dataset
        final_kmeans = KMeans(n_clusters=best_k, random_state=42, n_init=10)
        self.labels = final_kmeans.fit_predict(scaled_data)
        
        # Evaluate on full data
        final_score = silhouette_score(scaled_data, self.labels)
        
        print(f"Optimal clusters: {best_k}")
        print(f"Sample silhouette: {best_score:.3f}")
        print(f"Full data silhouette: {final_score:.3f}")
        
        return self.labels
    
    def get_classification_stats(self):
        """Get statistics about the classification quality"""
        scaled_data = StandardScaler().fit_transform(self.data)
        
        # Cluster probabilities for uncertainty analysis
        probs = self.gmm.predict_proba(scaled_data)
        max_probs = np.max(probs, axis=1)
        
        # Cluster sizes
        unique_labels, counts = np.unique(self.labels, return_counts=True)
        
        stats: dict[str, int | float | dict[np.ndarray, np.ndarray] | np.floating] = {
            'n_clusters': len(unique_labels),
            'cluster_sizes': dict(zip(unique_labels, counts)),
            'avg_cluster_size': np.mean(counts),
            'cluster_size_std': np.std(counts),
            'avg_confidence': np.mean(max_probs),
            'min_confidence': np.min(max_probs),
            'low_confidence_pct': np.mean(max_probs < 0.5) * 100,
            # 'silhouette_score': self._silhouette_score(scaled_data, self.unique_labels),
            'bic_score': self.gmm.bic(scaled_data),
            'aic_score': self.gmm.aic(scaled_data)
        }
        
        return stats
    

    def _silhouette_score(self, data: np.ndarray, labels: np.ndarray):
        """Calculate silhouette score"""
        try:
            return silhouette_score(data, labels)
        except:
            return None

    def plot_classification_quality(self) -> None:
        """Plot various classification quality metrics"""
        
        _fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        # Cluster size distribution
        unique_labels, counts = np.unique(self.labels, return_counts=True)
        axes[0,0].bar(unique_labels, counts)
        axes[0,0].set_title('Cluster Sizes')
        axes[0,0].set_xlabel('Cluster ID')
        axes[0,0].set_ylabel('Count')
        
        # Prediction confidence distribution
        scaled_data = StandardScaler().fit_transform(self.data)
        probs = self.gmm.predict_proba(scaled_data)
        max_probs = np.max(probs, axis=1)
        axes[0,1].hist(max_probs, bins=50, alpha=0.7)
        axes[0,1].set_title('Prediction Confidence Distribution')
        axes[0,1].set_xlabel('Max Probability')
        axes[0,1].set_ylabel('Frequency')
        axes[0,1].axvline(0.5, color='red', linestyle='--', label='50% threshold')
        axes[0,1].legend()
        
        # 2D visualization using PCA
        if self.data.shape[1] > 2:
            pca = PCA(n_components=2)
            data_2d = pca.fit_transform(scaled_data)
        else:
            data_2d = scaled_data
        
        _scatter = axes[1,0].scatter(data_2d[:, 0], data_2d[:, 1], c=self.labels, cmap='tab10', alpha=0.6)
        axes[1,0].set_title('Clusters in 2D (PCA if needed)')
        axes[1,0].set_xlabel('Component 1')
        axes[1,0].set_ylabel('Component 2')
        
        # Confidence by cluster
        cluster_confidences = []
        for cluster_id in unique_labels:
            mask = self.labels == cluster_id
            cluster_confidences.append(np.mean(max_probs[mask]))
        
        axes[1,1].bar(unique_labels, cluster_confidences)
        axes[1,1].set_title('Average Confidence by Cluster')
        axes[1,1].set_xlabel('Cluster ID')
        axes[1,1].set_ylabel('Average Confidence')
        
        plt.tight_layout()
        plt.show()

# cwd = Path.cwd()
# dl = DataLoader()
# dl.load_data_from_path(cwd/'data'/'SPY'/'tiingo'/'historical_pct.jsonl')

# data = dl.df

# window_size = 5
# windows = []
# for i in range(0, len(data) - window_size + 1, 1):
#     window = data.iloc[i:i+window_size].values.flatten()
#     windows.append(window)
# windows = np.array(windows)

# def penalized_bic(gmm: GaussianMixture, data: np.ndarray):
#     base_bic = gmm.bic(data)
    
#     # Penalize ill-conditioned covariance matrices
#     condition_penalty = 0
#     for cov in gmm.covariances_:
#         try:
#             cond_num = np.linalg.cond(cov)
#             if cond_num > 1e12:  # Threshold for numerical instability
#                 condition_penalty += 1000 * np.log(cond_num)
#         except:
#             condition_penalty += 1e6  # Severe penalty for singular matrices
    
#     return base_bic + condition_penalty







# windows = StandardScaler().fit_transform(windows)

# n_components_range = range(19, 30) # ConvergenceWarning for n_components > 20
# bic_scores = []

# best_gmm = None
# best_bic = float('inf')

# for n in n_components_range:
#     print(n)
#     gmm = GaussianMixture(n_components=n, covariance_type='diag', reg_covar=1e-6)
#     gmm.fit(windows)
#     bic = gmm.bic(windows)
#     bic_scores.append(bic)
        
#     if bic < best_bic:
#         best_bic = bic
#         best_gmm = gmm

# print(bic_scores)
# # Save the trained GMM model
# with open(cwd/'analysis/tokenization/visualizations/gmm_model.pkl', 'wb') as f:
#     pickle.dump(best_gmm, f)
