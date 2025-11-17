"""
Prediction Pipeline Service

Orchestrates all prediction models to generate match predictions:
- Calculates team statistics from historical data
- Runs predictions through tier-appropriate models
- Stores predictions in database
- Provides tier-based access to predictions
"""

import asyncio
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
import logging

from app.models.fixture import Fixture, FixtureStat
from app.models.team import Team
from app.models.league import League
from app.models.prediction import Prediction, TeamRating
from app.ml.statistical.poisson import PoissonModel
from app.ml.statistical.dixon_coles import DixonColesModel
from app.ml.statistical.elo import EloModel

logger = logging.getLogger(__name__)


# Statistical model tier mapping (always available as fallback)
STATISTICAL_MODEL_TIER_MAP = {
    "free": ["poisson"],
    "starter": ["poisson", "dixon_coles"],
    "pro": ["poisson", "dixon_coles", "elo"],
    "premium": ["poisson", "dixon_coles", "elo", "logistic"],
    "ultimate": ["poisson", "dixon_coles", "elo", "logistic", "random_forest", "xgboost"]
}


class PredictionPipeline:
    """Service for generating predictions from synced data."""

    def __init__(self, db: Session, use_ml_models: bool = True):
        """
        Initialize Prediction Pipeline.

        Args:
            db: Database session
            use_ml_models: Whether to use ML models (default: True)
        """
        self.db = db
        self.use_ml_models = use_ml_models

        # Statistical models (always available)
        self.poisson = PoissonModel()
        self.dixon_coles = DixonColesModel()
        self.elo = EloModel()

        # ML models (lazy loaded)
        self._ml_service = None
        if use_ml_models:
            try:
                from app.services.ml_prediction_service import MLPredictionService
                self._ml_service = MLPredictionService(db)
                logger.info("✅ ML Prediction Service initialized with 22 models")
            except Exception as e:
                logger.warning(f"⚠️  ML models not available: {str(e)}")
                logger.info("📊 Falling back to statistical models only")
                self.use_ml_models = False

    def calculate_team_stats(
        self,
        team_id: int,
        league_id: int,
        season: int,
        num_matches: int = 10
    ) -> Dict:
        """
        Calculate team statistics from recent matches.

        Returns dict with:
        - goals_scored: Average goals scored per match
        - goals_conceded: Average goals conceded per match
        - attack_strength: Attacking strength rating
        - defense_strength: Defensive strength rating
        """
        # Get recent home matches
        home_fixtures = self.db.query(Fixture).filter(
            and_(
                Fixture.home_team_id == team_id,
                Fixture.league_id == league_id,
                Fixture.season == season,
                Fixture.status.in_(["FT", "AET", "PEN"])
            )
        ).order_by(Fixture.match_date.desc()).limit(num_matches).all()

        # Get recent away matches
        away_fixtures = self.db.query(Fixture).filter(
            and_(
                Fixture.away_team_id == team_id,
                Fixture.league_id == league_id,
                Fixture.season == season,
                Fixture.status.in_(["FT", "AET", "PEN"])
            )
        ).order_by(Fixture.match_date.desc()).limit(num_matches).all()

        # Calculate statistics
        home_goals_scored = []
        home_goals_conceded = []
        away_goals_scored = []
        away_goals_conceded = []

        for fixture in home_fixtures:
            if fixture.score:
                home_goals_scored.append(fixture.score.home_fulltime or 0)
                home_goals_conceded.append(fixture.score.away_fulltime or 0)

        for fixture in away_fixtures:
            if fixture.score:
                away_goals_scored.append(fixture.score.away_fulltime or 0)
                away_goals_conceded.append(fixture.score.home_fulltime or 0)

        # Calculate averages
        all_scored = home_goals_scored + away_goals_scored
        all_conceded = home_goals_conceded + away_goals_conceded

        avg_goals_scored = sum(all_scored) / len(all_scored) if all_scored else 1.0
        avg_goals_conceded = sum(all_conceded) / len(all_conceded) if all_conceded else 1.0

        # Calculate league averages for strength calculation
        league_avg_goals = self._get_league_average_goals(league_id, season)

        attack_strength = avg_goals_scored / league_avg_goals if league_avg_goals > 0 else 1.0
        defense_strength = avg_goals_conceded / league_avg_goals if league_avg_goals > 0 else 1.0

        return {
            "goals_scored": avg_goals_scored,
            "goals_conceded": avg_goals_conceded,
            "attack_strength": attack_strength,
            "defense_strength": defense_strength,
            "matches_analyzed": len(all_scored)
        }

    def _get_league_average_goals(self, league_id: int, season: int) -> float:
        """Calculate average goals per match in a league."""
        fixtures = self.db.query(Fixture).filter(
            and_(
                Fixture.league_id == league_id,
                Fixture.season == season,
                Fixture.status.in_(["FT", "AET", "PEN"])
            )
        ).all()

        if not fixtures:
            return 1.5  # Default average

        total_goals = 0
        count = 0

        for fixture in fixtures:
            if fixture.score:
                home_goals = fixture.score.home_fulltime or 0
                away_goals = fixture.score.away_fulltime or 0
                total_goals += (home_goals + away_goals)
                count += 1

        return (total_goals / count) if count > 0 else 1.5

    def generate_prediction(
        self,
        fixture_id: int,
        user_tier: str = "free"
    ) -> Dict:
        """
        Generate ML predictions for a fixture based on user tier.

        IMPORTANT: Predictions are calculated ONLY from database statistics:
        - Historical match results (Fixture table)
        - Team performance metrics (goals scored/conceded)
        - Attack/defense strength ratios
        - Elo ratings (calculated from past results)

        This method NEVER uses bookmaker odds or any external prediction data.
        All calculations are purely statistical from your historical database.

        Args:
            fixture_id: Fixture to predict
            user_tier: User subscription tier (determines available models)

        Returns:
            Dictionary with predictions from all tier-appropriate models
        """
        # Get fixture
        fixture = self.db.query(Fixture).filter(Fixture.id == fixture_id).first()
        if not fixture:
            raise ValueError(f"Fixture {fixture_id} not found")

        # Get team stats
        home_stats = self.calculate_team_stats(
            fixture.home_team_id,
            fixture.league_id,
            fixture.season
        )
        away_stats = self.calculate_team_stats(
            fixture.away_team_id,
            fixture.league_id,
            fixture.season
        )

        # Get available models for tier
        available_statistical = STATISTICAL_MODEL_TIER_MAP.get(user_tier, ["poisson"])

        predictions = {}
        models_used = []

        # Run Poisson model (available to all tiers)
        if "poisson" in available_statistical:
            poisson_pred = self.poisson.predict(
                home_attack=home_stats["attack_strength"],
                home_defense=home_stats["defense_strength"],
                away_attack=away_stats["attack_strength"],
                away_defense=away_stats["defense_strength"]
            )
            predictions["poisson"] = poisson_pred
            models_used.append("poisson")

        # Run Dixon-Coles (starter+)
        if "dixon_coles" in available_statistical:
            dc_pred = self.dixon_coles.predict(
                home_attack=home_stats["attack_strength"],
                home_defense=home_stats["defense_strength"],
                away_attack=away_stats["attack_strength"],
                away_defense=away_stats["defense_strength"]
            )
            predictions["dixon_coles"] = dc_pred
            models_used.append("dixon_coles")

        # Run Elo (pro+)
        if "elo" in available_statistical:
            try:
                home_rating = self._get_team_rating(fixture.home_team_id, fixture.league_id, fixture.season)
                away_rating = self._get_team_rating(fixture.away_team_id, fixture.league_id, fixture.season)

                elo_pred = self.elo.predict(home_rating, away_rating)
                predictions["elo"] = elo_pred
                models_used.append("elo")
            except Exception as e:
                logger.error(f"Elo prediction error: {str(e)}")

        # ==============================================
        # PART 2: MACHINE LEARNING MODELS (22 models)
        # ==============================================

        ml_predictions = {}
        if self.use_ml_models and self._ml_service:
            try:
                ml_result = self._ml_service.predict(
                    fixture_id=fixture_id,
                    user_tier=user_tier
                )

                # Merge ML predictions
                ml_predictions = ml_result.get("predictions", {})
                predictions.update(ml_predictions)
                models_used.extend(ml_result.get("models_used", []))

                logger.info(f"🤖 ML models used: {len(ml_predictions)} for tier '{user_tier}'")
            except Exception as e:
                logger.warning(f"⚠️  ML prediction failed: {str(e)}")

        # Calculate unified consensus from ALL predictions
        consensus = self._calculate_consensus(predictions)

        result = {
            "fixture_id": fixture_id,
            "home_team_id": fixture.home_team_id,
            "away_team_id": fixture.away_team_id,
            "league_id": fixture.league_id,
            "match_date": fixture.match_date.isoformat() if fixture.match_date else None,
            "home_stats": home_stats,
            "away_stats": away_stats,
            "predictions": predictions,
            "consensus": consensus,
            "tier": user_tier,
            "models_used": models_used,
            "total_models": len(predictions),
            "statistical_models": len([m for m in models_used if m in ["poisson", "dixon_coles", "elo"]]),
            "ml_models": len(ml_predictions),
            "has_ml_predictions": len(ml_predictions) > 0
        }

        return result

    def _get_team_rating(self, team_id: int, league_id: int, season: int) -> float:
        """Get team's Elo rating, or default if not found."""
        rating = self.db.query(TeamRating).filter(
            and_(
                TeamRating.team_id == team_id,
                TeamRating.league_id == league_id,
                TeamRating.season == season
            )
        ).first()

        return rating.elo_rating if rating else 1500.0  # Default Elo

    def _calculate_consensus(self, predictions: Dict) -> Dict:
        """Calculate consensus prediction from multiple models."""
        home_win_probs = []
        draw_probs = []
        away_win_probs = []

        for model_name, pred in predictions.items():
            if "probabilities" in pred:
                home_win_probs.append(pred["probabilities"]["home_win"])
                draw_probs.append(pred["probabilities"]["draw"])
                away_win_probs.append(pred["probabilities"]["away_win"])

        if not home_win_probs:
            return {}

        avg_home = sum(home_win_probs) / len(home_win_probs)
        avg_draw = sum(draw_probs) / len(draw_probs)
        avg_away = sum(away_win_probs) / len(away_win_probs)

        # Determine recommended bet
        max_prob = max(avg_home, avg_draw, avg_away)
        if max_prob == avg_home:
            recommendation = "Home Win"
        elif max_prob == avg_draw:
            recommendation = "Draw"
        else:
            recommendation = "Away Win"

        return {
            "home_win": round(avg_home * 100, 2),
            "draw": round(avg_draw * 100, 2),
            "away_win": round(avg_away * 100, 2),
            "recommendation": recommendation,
            "confidence": round(max_prob * 100, 2)
        }

    def store_prediction(self, prediction_data: Dict, user_id: str) -> Prediction:
        """Store prediction in database."""
        try:
            # Check if prediction already exists
            existing = self.db.query(Prediction).filter(
                and_(
                    Prediction.fixture_id == prediction_data["fixture_id"],
                    Prediction.user_id == user_id
                )
            ).first()

            if existing:
                # Update existing prediction
                existing.poisson_home_win = prediction_data["predictions"].get("poisson", {}).get("probabilities", {}).get("home_win")
                existing.poisson_draw = prediction_data["predictions"].get("poisson", {}).get("probabilities", {}).get("draw")
                existing.poisson_away_win = prediction_data["predictions"].get("poisson", {}).get("probabilities", {}).get("away_win")
                existing.consensus_home_win = prediction_data["consensus"].get("home_win")
                existing.consensus_draw = prediction_data["consensus"].get("draw")
                existing.consensus_away_win = prediction_data["consensus"].get("away_win")
                existing.recommended_bet = prediction_data["consensus"].get("recommendation")
                existing.confidence_score = prediction_data["consensus"].get("confidence")
                existing.updated_at = datetime.utcnow()

                self.db.commit()
                return existing

            # Create new prediction
            prediction = Prediction(
                fixture_id=prediction_data["fixture_id"],
                user_id=user_id,
                poisson_home_win=prediction_data["predictions"].get("poisson", {}).get("probabilities", {}).get("home_win"),
                poisson_draw=prediction_data["predictions"].get("poisson", {}).get("probabilities", {}).get("draw"),
                poisson_away_win=prediction_data["predictions"].get("poisson", {}).get("probabilities", {}).get("away_win"),
                consensus_home_win=prediction_data["consensus"].get("home_win"),
                consensus_draw=prediction_data["consensus"].get("draw"),
                consensus_away_win=prediction_data["consensus"].get("away_win"),
                recommended_bet=prediction_data["consensus"].get("recommendation"),
                confidence_score=prediction_data["consensus"].get("confidence")
            )

            self.db.add(prediction)
            self.db.commit()
            self.db.refresh(prediction)

            return prediction

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error storing prediction: {str(e)}")
            raise

    def generate_predictions_for_upcoming(
        self,
        league_id: Optional[int] = None,
        days_ahead: int = 7,
        user_tier: str = "free"
    ) -> List[Dict]:
        """
        Generate predictions for upcoming fixtures.

        Args:
            league_id: Optional filter by league
            days_ahead: Number of days to look ahead
            user_tier: User subscription tier

        Returns:
            List of prediction dictionaries
        """
        # Get upcoming fixtures
        end_date = datetime.now() + timedelta(days=days_ahead)

        query = self.db.query(Fixture).filter(
            and_(
                Fixture.match_date >= datetime.now(),
                Fixture.match_date <= end_date,
                Fixture.status == "NS"  # Not Started
            )
        )

        if league_id:
            query = query.filter(Fixture.league_id == league_id)

        fixtures = query.order_by(Fixture.match_date).all()

        predictions = []
        for fixture in fixtures:
            try:
                pred = self.generate_prediction(fixture.id, user_tier)
                predictions.append(pred)
            except Exception as e:
                logger.error(f"Error generating prediction for fixture {fixture.id}: {str(e)}")
                continue

        return predictions

    def update_team_ratings(self, league_id: int, season: int):
        """
        Update Elo ratings for all teams in a league after matches complete.

        Should be called after fixture data is updated.
        """
        # Get all finished fixtures for the league/season
        fixtures = self.db.query(Fixture).filter(
            and_(
                Fixture.league_id == league_id,
                Fixture.season == season,
                Fixture.status.in_(["FT", "AET", "PEN"])
            )
        ).order_by(Fixture.match_date).all()

        for fixture in fixtures:
            if not fixture.score:
                continue

            home_goals = fixture.score.home_fulltime or 0
            away_goals = fixture.score.away_fulltime or 0

            # Determine result
            if home_goals > away_goals:
                result = 1.0  # Home win
            elif home_goals < away_goals:
                result = 0.0  # Away win
            else:
                result = 0.5  # Draw

            # Get current ratings
            home_rating_obj = self._get_or_create_rating(fixture.home_team_id, league_id, season)
            away_rating_obj = self._get_or_create_rating(fixture.away_team_id, league_id, season)

            # Update ratings using Elo model
            new_home_rating, new_away_rating = self.elo.update_ratings(
                home_rating_obj.elo_rating,
                away_rating_obj.elo_rating,
                result
            )

            home_rating_obj.elo_rating = new_home_rating
            away_rating_obj.elo_rating = new_away_rating

        self.db.commit()
        logger.info(f"Updated ratings for league {league_id}, season {season}")

    def _get_or_create_rating(self, team_id: int, league_id: int, season: int) -> TeamRating:
        """Get or create team rating record."""
        rating = self.db.query(TeamRating).filter(
            and_(
                TeamRating.team_id == team_id,
                TeamRating.league_id == league_id,
                TeamRating.season == season
            )
        ).first()

        if not rating:
            rating = TeamRating(
                team_id=team_id,
                league_id=league_id,
                season=season,
                elo_rating=1500.0,  # Default starting rating
                attack_rating=1.0,
                defense_rating=1.0
            )
            self.db.add(rating)
            self.db.commit()

        return rating
