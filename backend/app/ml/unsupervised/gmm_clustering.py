"""Gaussian Mixture Model Clustering for Team Analysis."""

import numpy as np
from sklearn.mixture import GaussianMixture
from .base_clustering import BaseClusteringModel


class GMMTeamClusterer(BaseClusteringModel):
    """
    Gaussian Mixture Model clustering for teams.

    Probabilistic clustering - provides soft assignments.
    Each team has probability of belonging to each cluster.
    """

    def __init__(self, n_components: int = 5, random_state: int = 42):
        super().__init__("gmm", n_components)
        self.model = GaussianMixture(
            n_components=n_components,
            covariance_type='full',
            random_state=random_state
        )

    def fit(self, X: np.ndarray) -> 'GMMTeamClusterer':
        """Fit GMM model."""
        self.model.fit(X)
        self.labels_ = self.model.predict(X)
        self.is_fitted = True
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict cluster labels."""
        if not self.is_fitted:
            raise ValueError("Model must be fitted first")
        return self.model.predict(X)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Get soft cluster assignments (probabilities).

        Returns:
            Array of shape (n_samples, n_clusters) with probabilities
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted first")
        return self.model.predict_proba(X)


# Global instance
gmm_clusterer = GMMTeamClusterer()
