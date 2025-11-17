"""K-Means Clustering for Team Analysis."""

import numpy as np
from sklearn.cluster import KMeans
from typing import Optional
from .base_clustering import BaseMLClusteringModel


class KMeansTeamClusterer(BaseMLClusteringModel):
    """
    K-Means clustering for grouping teams by playing style.

    Groups teams into K clusters based on performance metrics.
    Good for: Identifying similar teams, scouting, tactical analysis.
    """

    def __init__(self, n_clusters: int = 5, random_state: int = 42):
        super().__init__("kmeans", n_clusters)
        self.model = KMeans(
            n_clusters=n_clusters,
            init='k-means++',
            n_init=10,
            max_iter=300,
            random_state=random_state
        )

    def get_cluster_centers(self) -> Optional[np.ndarray]:
        """Get cluster centroids."""
        if self.is_fitted:
            return self.model.cluster_centers_
        return None


# Global instance
kmeans_clusterer = KMeansTeamClusterer()
