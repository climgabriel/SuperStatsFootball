"""Principal Component Analysis for Feature Reduction."""

import numpy as np
from sklearn.decomposition import PCA
from typing import Dict, List, Optional


class PCAMatchReducer:
    """
    PCA for dimensionality reduction of match features.

    Reduces 70+ features to ~10 principal components while
    retaining most variance. Useful for:
    - Visualization
    - Noise reduction
    - Speeding up other models
    """

    def __init__(self, n_components: int = 10, random_state: int = 42):
        """
        Initialize PCA reducer.

        Args:
            n_components: Number of principal components to keep
            random_state: Random seed
        """
        self.n_components = n_components
        self.model = PCA(n_components=n_components, random_state=random_state)
        self.is_fitted = False

    def fit(self, X: np.ndarray) -> 'PCAMatchReducer':
        """Fit PCA model to data."""
        self.model.fit(X)
        self.is_fitted = True
        return self

    def transform(self, X: np.ndarray) -> np.ndarray:
        """Transform data to principal components."""
        if not self.is_fitted:
            raise ValueError("Model must be fitted first")
        return self.model.transform(X)

    def fit_transform(self, X: np.ndarray) -> np.ndarray:
        """Fit and transform in one step."""
        self.fit(X)
        return self.transform(X)

    def inverse_transform(self, X_pca: np.ndarray) -> np.ndarray:
        """Transform back to original feature space."""
        if not self.is_fitted:
            raise ValueError("Model must be fitted first")
        return self.model.inverse_transform(X_pca)

    def get_explained_variance(self) -> Dict[str, any]:
        """
        Get variance explained by each component.

        Returns:
            Dictionary with variance information
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted first")

        return {
            "explained_variance_ratio": self.model.explained_variance_ratio_.tolist(),
            "cumulative_variance": np.cumsum(self.model.explained_variance_ratio_).tolist(),
            "total_variance_retained": float(np.sum(self.model.explained_variance_ratio_)),
            "n_components": self.n_components
        }

    def get_feature_importance(
        self,
        feature_names: Optional[List[str]] = None,
        component_idx: int = 0
    ) -> Dict[str, float]:
        """
        Get feature importance for a specific component.

        Args:
            feature_names: Names of original features
            component_idx: Which principal component (0-based)

        Returns:
            Dictionary mapping feature names to importance
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted first")

        if component_idx >= self.n_components:
            raise ValueError(f"component_idx must be < {self.n_components}")

        loadings = self.model.components_[component_idx]

        if feature_names is None:
            feature_names = [f"feature_{i}" for i in range(len(loadings))]

        # Sort by absolute loading value
        importance = dict(zip(feature_names, np.abs(loadings)))
        importance = {k: float(v) for k, v in sorted(importance.items(), key=lambda x: abs(x[1]), reverse=True)}

        return importance


# Global instance
pca_reducer = PCAMatchReducer()
