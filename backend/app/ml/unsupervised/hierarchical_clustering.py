"""Hierarchical Clustering for Team Analysis."""

import numpy as np
from sklearn.cluster import AgglomerativeClustering
from .base_clustering import BaseMLClusteringModel


class HierarchicalTeamClusterer(BaseMLClusteringModel):
    """
    Hierarchical (Agglomerative) clustering for teams.

    Builds hierarchy of clusters. Useful for understanding
    league structure and team relationships.
    """

    def __init__(self, n_clusters: int = 5, linkage: str = 'ward'):
        super().__init__("hierarchical", n_clusters)
        self.model = AgglomerativeClustering(
            n_clusters=n_clusters,
            linkage=linkage
        )


# Global instance
hierarchical_clusterer = HierarchicalTeamClusterer()
