"""
Base class for clustering models.

Provides common interface for team clustering algorithms.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
import numpy as np
import pandas as pd


class BaseClusteringModel(ABC):
    """
    Abstract base class for team clustering models.

    Clustering models group teams based on their characteristics
    (playing style, performance metrics, etc.).
    """

    def __init__(self, model_name: str, n_clusters: int = 5):
        """
        Initialize clustering model.

        Args:
            model_name: Name of the clustering algorithm
            n_clusters: Number of clusters (not used by all algorithms)
        """
        self.model_name = model_name
        self.n_clusters = n_clusters
        self.model = None
        self.labels_ = None
        self.is_fitted = False

    @abstractmethod
    def fit(self, X: np.ndarray) -> 'BaseClusteringModel':
        """
        Fit clustering model to data.

        Args:
            X: Feature matrix (n_teams, n_features)

        Returns:
            Self for method chaining
        """
        pass

    @abstractmethod
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Predict cluster labels for new data.

        Args:
            X: Feature matrix (n_teams, n_features)

        Returns:
            Cluster labels array
        """
        pass

    def fit_predict(self, X: np.ndarray) -> np.ndarray:
        """
        Fit model and return cluster labels.

        Args:
            X: Feature matrix

        Returns:
            Cluster labels
        """
        self.fit(X)
        return self.labels_

    def get_cluster_characteristics(
        self,
        X: np.ndarray,
        feature_names: Optional[List[str]] = None
    ) -> Dict[int, Dict[str, float]]:
        """
        Get characteristics of each cluster.

        Args:
            X: Feature matrix used for clustering
            feature_names: Names of features

        Returns:
            Dictionary mapping cluster_id to feature statistics
        """
        if not self.is_fitted or self.labels_ is None:
            raise ValueError("Model must be fitted before getting characteristics")

        if feature_names is None:
            feature_names = [f"feature_{i}" for i in range(X.shape[1])]

        characteristics = {}

        for cluster_id in np.unique(self.labels_):
            cluster_mask = self.labels_ == cluster_id
            cluster_data = X[cluster_mask]

            # Calculate mean values for each feature in this cluster
            cluster_stats = {}
            for i, fname in enumerate(feature_names):
                cluster_stats[fname] = {
                    "mean": float(np.mean(cluster_data[:, i])),
                    "std": float(np.std(cluster_data[:, i])),
                    "min": float(np.min(cluster_data[:, i])),
                    "max": float(np.max(cluster_data[:, i]))
                }

            characteristics[int(cluster_id)] = {
                "n_teams": int(np.sum(cluster_mask)),
                "features": cluster_stats
            }

        return characteristics

    def get_cluster_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics about clustering.

        Returns:
            Dictionary with clustering metrics
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted first")

        unique_labels = np.unique(self.labels_)

        # Count teams per cluster
        cluster_sizes = {}
        for label in unique_labels:
            cluster_sizes[int(label)] = int(np.sum(self.labels_ == label))

        return {
            "model": self.model_name,
            "n_clusters": len(unique_labels),
            "cluster_sizes": cluster_sizes,
            "total_teams": len(self.labels_),
            "is_fitted": self.is_fitted
        }


class BaseMLClusteringModel(BaseClusteringModel):
    """
    Base class for scikit-learn based clustering models.

    Provides common functionality for sklearn clustering algorithms.
    """

    def __init__(self, model_name: str, n_clusters: int = 5):
        super().__init__(model_name, n_clusters)

    def fit(self, X: np.ndarray) -> 'BaseMLClusteringModel':
        """Fit sklearn clustering model."""
        if self.model is None:
            raise ValueError("Model not initialized")

        self.model.fit(X)
        self.labels_ = self.model.labels_
        self.is_fitted = True
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict cluster labels."""
        if not self.is_fitted:
            raise ValueError("Model must be fitted first")

        # Note: Not all clustering algorithms support predict()
        # For those that don't, we'll return the closest cluster
        if hasattr(self.model, 'predict'):
            return self.model.predict(X)
        else:
            # Fall back to finding nearest cluster center
            return self._predict_nearest_cluster(X)

    def _predict_nearest_cluster(self, X: np.ndarray) -> np.ndarray:
        """
        Predict by finding nearest cluster center.

        Used for algorithms that don't have predict() method.
        """
        if hasattr(self.model, 'cluster_centers_'):
            # Calculate distances to all cluster centers
            centers = self.model.cluster_centers_
            distances = np.sqrt(((X[:, np.newaxis] - centers) ** 2).sum(axis=2))
            return np.argmin(distances, axis=1)
        else:
            raise NotImplementedError(
                f"{self.model_name} does not support prediction on new data"
            )
