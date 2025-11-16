"""
ML Prediction Service

Unified interface for generating predictions using all 22 ML models.
Integrates feature engineering with model predictions.

IMPORTANT: All predictions use ONLY database data - NO bookmaker odds.
"""

from typing import Dict, List, Optional
import numpy as np
from sqlalchemy.orm import Session
import logging
import os

from app.ml.features.feature_engineering import FeatureEngineer
from app.ml.machine_learning import create_all_models, get_tier_models
from app.models.fixture import Fixture

logger = logging.getLogger(__name__)


class MLPredictionService:
    """Service for ML-based match predictions."""

    def __init__(self, db: Session, models_dir: str = "models/trained"):
        """
        Initialize ML Prediction Service.

        Args:
            db: Database session
            models_dir: Directory where trained models are saved
        """
        self.db = db
        self.models_dir = models_dir
        self.feature_engineer = FeatureEngineer(db)
        self.all_models = create_all_models()
        self._load_trained_models()

    def _load_trained_models(self):
        """Load pre-trained models from disk if available."""
        if not os.path.exists(self.models_dir):
            logger.warning(f"Models directory not found: {self.models_dir}")
            logger.warning("Models will need to be trained before use")
            return

        for model_name, model in self.all_models.items():
            model_path = os.path.join(self.models_dir, f"{model_name}.pkl")
            if os.path.exists(model_path):
                try:
                    model.load(model_path)
                    logger.info(f"Loaded trained model: {model_name}")
                except Exception as e:
                    logger.error(f"Error loading {model_name}: {str(e)}")

    def predict(
        self,
        fixture_id: int,
        user_tier: str = "free",
        lookback_matches: int = 10
    ) -> Dict:
        """
        Generate ML predictions for a fixture.

        Args:
            fixture_id: Fixture ID to predict
            user_tier: User subscription tier
            lookback_matches: Number of recent matches to analyze

        Returns:
            Dictionary with predictions from all tier-appropriate models
        """
        # Get fixture
        fixture = self.db.query(Fixture).filter(Fixture.id == fixture_id).first()
        if not fixture:
            raise ValueError(f"Fixture {fixture_id} not found")

        # Extract features from database (NO ODDS!)
        features = self.feature_engineer.extract_features(
            home_team_id=fixture.home_team_id,
            away_team_id=fixture.away_team_id,
            league_id=fixture.league_id,
            season=fixture.season,
            lookback_matches=lookback_matches
        )

        feature_array = features["feature_array"]

        # Get models available for this tier
        available_model_names = get_tier_models(user_tier)

        predictions = {}

        for model_name in available_model_names:
            if model_name not in self.all_models:
                logger.warning(f"Model {model_name} not found in available models")
                continue

            model = self.all_models[model_name]

            if not model.is_trained:
                logger.warning(f"Model {model_name} is not trained, skipping")
                continue

            try:
                prediction = model.predict(feature_array)
                predictions[model_name] = prediction
            except Exception as e:
                logger.error(f"Error predicting with {model_name}: {str(e)}")
                continue

        # Calculate consensus from all model predictions
        consensus = self._calculate_consensus(predictions)

        return {
            "fixture_id": fixture_id,
            "home_team_id": fixture.home_team_id,
            "away_team_id": fixture.away_team_id,
            "predictions": predictions,
            "consensus": consensus,
            "tier": user_tier,
            "models_used": list(predictions.keys()),
            "total_models": len(predictions),
            "features_extracted": features["total_features"]
        }

    def _calculate_consensus(self, predictions: Dict) -> Dict:
        """
        Calculate consensus prediction from multiple models.

        Uses weighted average based on model confidence.
        """
        if not predictions:
            return {
                "home_win": 33.33,
                "draw": 33.33,
                "away_win": 33.33,
                "recommendation": "No prediction available",
                "confidence": 0.0
            }

        home_win_probs = []
        draw_probs = []
        away_win_probs = []
        weights = []

        for model_name, pred in predictions.items():
            if "probabilities" in pred:
                probs = pred["probabilities"]
                confidence = pred.get("confidence", 1.0)

                home_win_probs.append(probs["home_win"])
                draw_probs.append(probs["draw"])
                away_win_probs.append(probs["away_win"])
                weights.append(confidence)  # Weight by model confidence

        if not home_win_probs:
            return {
                "home_win": 33.33,
                "draw": 33.33,
                "away_win": 33.33,
                "recommendation": "No valid predictions",
                "confidence": 0.0
            }

        # Weighted average
        total_weight = sum(weights)
        weighted_home = sum(p * w for p, w in zip(home_win_probs, weights)) / total_weight
        weighted_draw = sum(p * w for p, w in zip(draw_probs, weights)) / total_weight
        weighted_away = sum(p * w for p, w in zip(away_win_probs, weights)) / total_weight

        # Determine recommendation
        max_prob = max(weighted_home, weighted_draw, weighted_away)
        if max_prob == weighted_home:
            recommendation = "Home Win"
        elif max_prob == weighted_draw:
            recommendation = "Draw"
        else:
            recommendation = "Away Win"

        return {
            "home_win": round(weighted_home * 100, 2),
            "draw": round(weighted_draw * 100, 2),
            "away_win": round(weighted_away * 100, 2),
            "recommendation": recommendation,
            "confidence": round(max_prob * 100, 2),
            "models_count": len(predictions)
        }

    def get_model_comparison(self, fixture_id: int, tier: str = "ultimate") -> Dict:
        """
        Compare predictions from all available models for analysis.

        Args:
            fixture_id: Fixture to analyze
            tier: Tier (use 'ultimate' to see all models)

        Returns:
            Detailed comparison of all model predictions
        """
        prediction_result = self.predict(fixture_id, tier)

        comparisons = []
        for model_name, pred in prediction_result["predictions"].items():
            probs = pred["probabilities"]
            comparisons.append({
                "model": model_name,
                "home_win": round(probs["home_win"] * 100, 2),
                "draw": round(probs["draw"] * 100, 2),
                "away_win": round(probs["away_win"] * 100, 2),
                "confidence": pred.get("confidence", 0) * 100,
                "prediction": max(probs, key=probs.get).replace("_", " ").title()
            })

        # Sort by confidence
        comparisons.sort(key=lambda x: x["confidence"], reverse=True)

        return {
            "fixture_id": fixture_id,
            "model_comparisons": comparisons,
            "consensus": prediction_result["consensus"],
            "total_models": len(comparisons)
        }

    def get_available_models(self, tier: str) -> List[str]:
        """Get list of model names available for a tier."""
        return get_tier_models(tier)

    def is_model_trained(self, model_name: str) -> bool:
        """Check if a specific model is trained."""
        if model_name not in self.all_models:
            return False
        return self.all_models[model_name].is_trained

    def get_training_status(self) -> Dict:
        """Get training status of all models."""
        status = {}
        for model_name, model in self.all_models.items():
            status[model_name] = {
                "trained": model.is_trained,
                "name": model.model_name
            }
        return status
