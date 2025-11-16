"""
Machine Learning Models for Football Prediction

Total: 22 ML models (+ 3 statistical = 25 total models)

All models use ONLY historical database data - NO bookmaker odds.
Models are distributed across 5 subscription tiers for optimal value.
"""

from .base_model import BaseMLModel
from .all_models import (
    # Core ML Models
    LogisticRegressionModel,
    RandomForestModel,
    XGBoostModel,
    GradientBoostingModel,
    SVMModel,
    KNNModel,
    DecisionTreeModel,
    NaiveBayesModel,
    AdaBoostModel,
    NeuralNetworkModel,
    LightGBMModel,
    CatBoostModel,
    ExtraTreesModel,
    RidgeClassifierModel,
    PassiveAggressiveModel,
    QDAModel,

    # Additional Advanced Models
    LDAModel,
    SGDModel,
    BaggingModel,
    GaussianProcessModel,

    # Meta-learning Ensembles
    StackingEnsembleModel,
    VotingEnsembleModel,

    # Utility functions
    create_all_models,
    get_tier_models
)

__all__ = [
    "BaseMLModel",

    # Core models (16)
    "LogisticRegressionModel",
    "RandomForestModel",
    "XGBoostModel",
    "GradientBoostingModel",
    "SVMModel",
    "KNNModel",
    "DecisionTreeModel",
    "NaiveBayesModel",
    "AdaBoostModel",
    "NeuralNetworkModel",
    "LightGBMModel",
    "CatBoostModel",
    "ExtraTreesModel",
    "RidgeClassifierModel",
    "PassiveAggressiveModel",
    "QDAModel",

    # Additional models (6)
    "LDAModel",
    "SGDModel",
    "BaggingModel",
    "GaussianProcessModel",
    "StackingEnsembleModel",
    "VotingEnsembleModel",

    # Utilities
    "create_all_models",
    "get_tier_models"
]
