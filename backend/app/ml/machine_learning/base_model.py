"""
Base Model Class for ML Football Predictions

All 17 ML models inherit from this base class for consistent interface.
"""

from abc import ABC, abstractmethod
from typing import Dict, Tuple, Optional
import numpy as np
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.calibration import CalibratedClassifierCV
import pickle
import os
import logging

logger = logging.getLogger(__name__)


class BaseMLModel(ABC):
    """Base class for all machine learning models."""

    def __init__(self, model_name: str):
        self.model_name = model_name
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_names = None
        self.calibrated_model = None

    @abstractmethod
    def _create_model(self):
        """Create the underlying sklearn/ML model. Must be implemented by subclasses."""
        pass

    def train(
        self,
        X: np.ndarray,
        y: np.ndarray,
        calibrate: bool = True,
        cv_folds: int = 5
    ) -> Dict:
        """
        Train the model on historical data.

        Args:
            X: Feature matrix (n_samples, n_features)
            y: Labels (0=away win, 1=draw, 2=home win)
            calibrate: Whether to calibrate probabilities using Platt scaling
            cv_folds: Number of cross-validation folds

        Returns:
            Dictionary with training metrics
        """
        logger.info(f"Training {self.model_name}...")

        # Initialize model if not done
        if self.model is None:
            self.model = self._create_model()

        # Scale features
        X_scaled = self.scaler.fit_transform(X)

        # Cross-validation before training
        cv = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=42)
        cv_scores = cross_val_score(self.model, X_scaled, y, cv=cv, scoring='accuracy')

        logger.info(f"{self.model_name} CV Accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")

        # Train on full dataset
        self.model.fit(X_scaled, y)

        # Calibrate probabilities for better probability estimates
        if calibrate:
            logger.info(f"Calibrating {self.model_name}...")
            self.calibrated_model = CalibratedClassifierCV(
                self.model,
                method='sigmoid',  # Platt scaling
                cv=3
            )
            self.calibrated_model.fit(X_scaled, y)

        self.is_trained = True

        return {
            "model_name": self.model_name,
            "cv_mean_accuracy": cv_scores.mean(),
            "cv_std_accuracy": cv_scores.std(),
            "cv_scores": cv_scores.tolist(),
            "trained": True,
            "calibrated": calibrate
        }

    def predict(self, X: np.ndarray) -> Dict:
        """
        Predict probabilities for a match.

        Args:
            X: Feature vector (1, n_features) or (n_samples, n_features)

        Returns:
            Dictionary with probabilities for home win, draw, away win
        """
        if not self.is_trained:
            raise ValueError(f"{self.model_name} is not trained yet")

        # Ensure X is 2D
        if len(X.shape) == 1:
            X = X.reshape(1, -1)

        # Scale features
        X_scaled = self.scaler.transform(X)

        # Use calibrated model if available, otherwise use base model
        model_to_use = self.calibrated_model if self.calibrated_model is not None else self.model

        # Get probabilities
        probs = model_to_use.predict_proba(X_scaled)[0]

        # Map to match outcomes (sklearn typically orders: 0, 1, 2)
        # 0 = away win, 1 = draw, 2 = home win
        return {
            "probabilities": {
                "home_win": float(probs[2]) if len(probs) > 2 else 0.33,
                "draw": float(probs[1]) if len(probs) > 1 else 0.33,
                "away_win": float(probs[0]) if len(probs) > 0 else 0.33
            },
            "model_name": self.model_name,
            "confidence": float(np.max(probs))
        }

    def predict_class(self, X: np.ndarray) -> int:
        """Predict the most likely outcome class."""
        if not self.is_trained:
            raise ValueError(f"{self.model_name} is not trained yet")

        if len(X.shape) == 1:
            X = X.reshape(1, -1)

        X_scaled = self.scaler.transform(X)
        return int(self.model.predict(X_scaled)[0])

    def save(self, path: str):
        """Save model to disk."""
        os.makedirs(os.path.dirname(path), exist_ok=True)

        model_data = {
            "model": self.model,
            "calibrated_model": self.calibrated_model,
            "scaler": self.scaler,
            "model_name": self.model_name,
            "is_trained": self.is_trained,
            "feature_names": self.feature_names
        }

        with open(path, 'wb') as f:
            pickle.dump(model_data, f)

        logger.info(f"Saved {self.model_name} to {path}")

    def load(self, path: str):
        """Load model from disk."""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Model file not found: {path}")

        with open(path, 'rb') as f:
            model_data = pickle.load(f)

        self.model = model_data["model"]
        self.calibrated_model = model_data.get("calibrated_model")
        self.scaler = model_data["scaler"]
        self.model_name = model_data["model_name"]
        self.is_trained = model_data["is_trained"]
        self.feature_names = model_data.get("feature_names")

        logger.info(f"Loaded {self.model_name} from {path}")

    def get_feature_importance(self) -> Optional[Dict]:
        """Get feature importance if model supports it."""
        if not hasattr(self.model, 'feature_importances_'):
            return None

        if self.feature_names is None:
            return None

        importances = self.model.feature_importances_
        feature_importance = {
            name: float(importance)
            for name, importance in zip(self.feature_names, importances)
        }

        # Sort by importance
        sorted_importance = dict(
            sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
        )

        return sorted_importance
