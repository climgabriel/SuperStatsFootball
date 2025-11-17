"""DBSCAN Clustering for Team Analysis."""

import numpy as np
from sklearn.cluster import DBSCAN
from .base_clustering import BaseMLClusteringModel


class DBSCANTeamClusterer(BaseMLClusteringModel):
    """
    DBSCAN (Density-Based) clustering for teams.

    Finds clusters of arbitrary shape and identifies outliers.
    Good for: Detecting unusual teams, form-based grouping.
    """

    def __init__(self, eps: float = 0.5, min_samples: int = 3):
        super().__init__("dbscan", n_clusters=None)
        self.eps = eps
        self.min_samples = min_samples
        self.model = DBSCAN(eps=eps, min_samples=min_samples)

    def get_outliers(self) -> np.ndarray:
        """Get indices of outlier teams (label = -1)."""
        if self.is_fitted:
            return np.where(self.labels_ == -1)[0]
        return np.array([])


# Global instance
dbscan_clusterer = DBSCANTeamClusterer()
