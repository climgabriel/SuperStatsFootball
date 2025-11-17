"""
Comprehensive Model Factory for All 36 Models

Provides unified interface to create any of the 36 prediction models.
"""

from typing import Dict, Any, Optional, List
import warnings

# Statistical Models (8)
from .statistical import (
    poisson_model,
    dixon_coles_model,
    elo_model,
    bivariate_poisson_model,
    skellam_model,
    negative_binomial_model,
    zero_inflated_poisson_model,
    cox_survival_model
)

# ML Models (22)
from .machine_learning import create_all_models

# Clustering Models (4)
from .unsupervised.kmeans_clustering import kmeans_clusterer
from .unsupervised.hierarchical_clustering import hierarchical_clusterer
from .unsupervised.dbscan_clustering import dbscan_clusterer
from .unsupervised.gmm_clustering import gmm_clusterer

# Dimensionality Reduction (1)
from .dimensionality_reduction.pca_reducer import pca_reducer

# Deep Learning (1)
try:
    from .deep_learning.lstm_model import lstm_outcome_model
    LSTM_AVAILABLE = lstm_outcome_model is not None
except ImportError:
    LSTM_AVAILABLE = False
    lstm_outcome_model = None


class ModelFactory:
    """
    Factory for creating and managing all 36 models.

    Provides:
    - Unified model creation
    - Model listing by category
    - Tier-based access control
    - Model metadata
    """

    # Model categories
    STATISTICAL = "statistical"
    MACHINE_LEARNING = "machine_learning"
    CLUSTERING = "clustering"
    DIMENSIONALITY_REDUCTION = "dimensionality_reduction"
    DEEP_LEARNING = "deep_learning"

    def __init__(self):
        """Initialize model factory."""
        self._ml_models = create_all_models()
        self._init_model_registry()

    def _init_model_registry(self):
        """Initialize registry of all 36 models."""
        self.models = {
            # Statistical Models (8)
            "poisson": {"instance": poisson_model, "category": self.STATISTICAL},
            "dixon_coles": {"instance": dixon_coles_model, "category": self.STATISTICAL},
            "elo": {"instance": elo_model, "category": self.STATISTICAL},
            "bivariate_poisson": {"instance": bivariate_poisson_model, "category": self.STATISTICAL},
            "skellam": {"instance": skellam_model, "category": self.STATISTICAL},
            "negative_binomial": {"instance": negative_binomial_model, "category": self.STATISTICAL},
            "zero_inflated_poisson": {"instance": zero_inflated_poisson_model, "category": self.STATISTICAL},
            "cox_survival": {"instance": cox_survival_model, "category": self.STATISTICAL},

            # ML Models (22) - from existing all_models.py
            **{name: {"instance": model, "category": self.MACHINE_LEARNING}
               for name, model in self._ml_models.items()},

            # Clustering Models (4)
            "kmeans": {"instance": kmeans_clusterer, "category": self.CLUSTERING},
            "hierarchical": {"instance": hierarchical_clusterer, "category": self.CLUSTERING},
            "dbscan": {"instance": dbscan_clusterer, "category": self.CLUSTERING},
            "gmm": {"instance": gmm_clusterer, "category": self.CLUSTERING},

            # Dimensionality Reduction (1)
            "pca": {"instance": pca_reducer, "category": self.DIMENSIONALITY_REDUCTION},
        }

        # Deep Learning (conditional)
        if LSTM_AVAILABLE:
            self.models["lstm"] = {
                "instance": lstm_outcome_model,
                "category": self.DEEP_LEARNING
            }

    def get_model(self, model_name: str):
        """
        Get model instance by name.

        Args:
            model_name: Name of the model

        Returns:
            Model instance

        Raises:
            ValueError: If model not found
        """
        if model_name not in self.models:
            raise ValueError(
                f"Model '{model_name}' not found. "
                f"Available models: {list(self.models.keys())}"
            )

        return self.models[model_name]["instance"]

    def list_models(
        self,
        category: Optional[str] = None,
        tier: Optional[str] = None
    ) -> List[str]:
        """
        List available models.

        Args:
            category: Filter by category (optional)
            tier: Filter by tier (optional)

        Returns:
            List of model names
        """
        model_names = []

        for name, info in self.models.items():
            # Filter by category
            if category and info["category"] != category:
                continue

            # Filter by tier
            if tier:
                tier_models = get_tier_models(tier)
                if name not in tier_models:
                    continue

            model_names.append(name)

        return sorted(model_names)

    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """
        Get metadata about a model.

        Args:
            model_name: Name of the model

        Returns:
            Dictionary with model information
        """
        if model_name not in self.models:
            raise ValueError(f"Model '{model_name}' not found")

        info = self.models[model_name].copy()
        model = info["instance"]

        # Add additional metadata
        info["name"] = model_name
        info["type"] = type(model).__name__

        # Check if model has certain attributes
        if hasattr(model, 'is_fitted'):
            info["is_fitted"] = model.is_fitted
        elif hasattr(model, 'model') and hasattr(model.model, 'is_fitted'):
            info["is_fitted"] = model.model.is_fitted
        else:
            info["is_fitted"] = None

        return info

    def count_models(self, category: Optional[str] = None) -> int:
        """Count models by category."""
        if category is None:
            return len(self.models)

        return len([m for m in self.models.values() if m["category"] == category])

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all models."""
        return {
            "total_models": len(self.models),
            "by_category": {
                self.STATISTICAL: self.count_models(self.STATISTICAL),
                self.MACHINE_LEARNING: self.count_models(self.MACHINE_LEARNING),
                self.CLUSTERING: self.count_models(self.CLUSTERING),
                self.DIMENSIONALITY_REDUCTION: self.count_models(self.DIMENSIONALITY_REDUCTION),
                self.DEEP_LEARNING: self.count_models(self.DEEP_LEARNING)
            },
            "categories": [
                self.STATISTICAL,
                self.MACHINE_LEARNING,
                self.CLUSTERING,
                self.DIMENSIONALITY_REDUCTION,
                self.DEEP_LEARNING
            ],
            "lstm_available": LSTM_AVAILABLE
        }


def get_tier_models(tier: str) -> List[str]:
    """
    Get model names available for each tier (Updated for 36 models).

    Total: 36 Models
    - Statistical: 8
    - ML (Supervised): 22
    - Clustering: 4
    - Dimensionality Reduction: 1
    - Deep Learning: 1

    Distribution:
    - Free: 7 models (3 statistical + 4 ML)
    - Starter: 15 models (5 statistical + 9 ML + 1 clustering)
    - Pro: 24 models (7 statistical + 15 ML + 2 clustering)
    - Premium: 32 models (8 statistical + 20 ML + 4 clustering)
    - Ultimate: 36 models (ALL)
    """

    tier_map = {
        "free": [
            # Statistical (3)
            "poisson", "dixon_coles", "elo",
            # ML (4)
            "logistic_regression", "decision_tree", "naive_bayes", "ridge"
        ],

        "starter": [
            # Free models (7)
            "poisson", "dixon_coles", "elo",
            "logistic_regression", "decision_tree", "naive_bayes", "ridge",
            # Add statistical (2)
            "bivariate_poisson", "skellam",
            # Add ML (5)
            "knn", "passive_aggressive", "qda", "lda", "sgd",
            # Add clustering (1)
            "kmeans"
        ],

        "pro": [
            # Starter models (15)
            "poisson", "dixon_coles", "elo", "bivariate_poisson", "skellam",
            "logistic_regression", "decision_tree", "naive_bayes", "ridge",
            "knn", "passive_aggressive", "qda", "lda", "sgd", "kmeans",
            # Add statistical (2)
            "negative_binomial", "zero_inflated_poisson",
            # Add ML (6)
            "random_forest", "extra_trees", "adaboost",
            "gradient_boosting", "neural_network", "bagging",
            # Add clustering (1)
            "hierarchical"
        ],

        "premium": [
            # Pro models (24)
            "poisson", "dixon_coles", "elo", "bivariate_poisson", "skellam",
            "negative_binomial", "zero_inflated_poisson",
            "logistic_regression", "decision_tree", "naive_bayes", "ridge",
            "knn", "passive_aggressive", "qda", "lda", "sgd",
            "random_forest", "extra_trees", "adaboost", "gradient_boosting",
            "neural_network", "bagging", "kmeans", "hierarchical",
            # Add statistical (1)
            "cox_survival",
            # Add ML (5)
            "xgboost", "lightgbm", "catboost", "svm", "stacking_ensemble",
            # Add clustering (2)
            "dbscan", "gmm"
        ],

        "ultimate": [
            # Premium models (32)
            "poisson", "dixon_coles", "elo", "bivariate_poisson", "skellam",
            "negative_binomial", "zero_inflated_poisson", "cox_survival",
            "logistic_regression", "decision_tree", "naive_bayes", "ridge",
            "knn", "passive_aggressive", "qda", "lda", "sgd",
            "random_forest", "extra_trees", "adaboost", "gradient_boosting",
            "neural_network", "bagging", "xgboost", "lightgbm", "catboost",
            "svm", "stacking_ensemble", "kmeans", "hierarchical", "dbscan", "gmm",
            # Add ML (2)
            "gaussian_process", "voting_ensemble",
            # Add dimensionality reduction (1)
            "pca",
            # Add deep learning (1)
            "lstm"
        ]
    }

    return tier_map.get(tier, tier_map["free"])


# Global factory instance
model_factory = ModelFactory()


__all__ = [
    "ModelFactory",
    "model_factory",
    "get_tier_models"
]
