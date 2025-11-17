"""
Base class for all statistical football prediction models.

Provides common interface and utilities for statistical models like
Poisson, Dixon-Coles, Skellam, etc.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import numpy as np


class BaseStatisticalModel(ABC):
    """
    Abstract base class for statistical football models.

    All statistical models should inherit from this class and implement
    the predict() method.
    """

    def __init__(self, model_name: str):
        """
        Initialize base statistical model.

        Args:
            model_name: Name of the model (e.g., "poisson", "dixon_coles")
        """
        self.model_name = model_name
        self.home_advantage = 1.3  # Default home advantage factor
        self.league_avg_goals = 1.4  # Average goals per team per match

    @abstractmethod
    def predict(
        self,
        home_attack: float,
        home_defense: float,
        away_attack: float,
        away_defense: float,
        home_advantage: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Generate prediction for a match.

        Args:
            home_attack: Home team's attacking strength (relative to league avg)
            home_defense: Home team's defensive strength (relative to league avg)
            away_attack: Away team's attacking strength
            away_defense: Away team's defensive strength
            home_advantage: Home advantage factor (optional, uses default if None)

        Returns:
            Dictionary containing:
                - probabilities: {home_win, draw, away_win}
                - predicted_home_score: Expected home goals
                - predicted_away_score: Expected away goals
                - most_likely_score: Most probable scoreline
                - model_details: Model-specific information
        """
        pass

    def calculate_team_strengths(
        self,
        goals_scored: int,
        goals_conceded: int,
        matches_played: int
    ) -> tuple[float, float]:
        """
        Calculate team's attacking and defensive strengths.

        Args:
            goals_scored: Total goals scored
            goals_conceded: Total goals conceded
            matches_played: Number of matches played

        Returns:
            Tuple of (attack_strength, defense_strength)
        """
        if matches_played == 0:
            return 1.0, 1.0

        attack_strength = (goals_scored / matches_played) / self.league_avg_goals
        defense_strength = (goals_conceded / matches_played) / self.league_avg_goals

        return attack_strength, defense_strength

    def _normalize_probabilities(self, probs: Dict[str, float]) -> Dict[str, float]:
        """
        Normalize probabilities to sum to 1.0.

        Args:
            probs: Dictionary of probabilities

        Returns:
            Normalized probabilities
        """
        total = sum(probs.values())
        if total == 0:
            return probs
        return {k: v / total for k, v in probs.items()}

    def _standard_response(
        self,
        home_win_prob: float,
        draw_prob: float,
        away_win_prob: float,
        home_expected: float,
        away_expected: float,
        most_likely_score: str,
        additional_details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create standard prediction response format.

        Args:
            home_win_prob: Probability of home win
            draw_prob: Probability of draw
            away_win_prob: Probability of away win
            home_expected: Expected home goals
            away_expected: Expected away goals
            most_likely_score: Most likely scoreline (e.g., "2-1")
            additional_details: Model-specific additional information

        Returns:
            Standardized prediction dictionary
        """
        response = {
            "probabilities": {
                "home_win": round(float(home_win_prob), 4),
                "draw": round(float(draw_prob), 4),
                "away_win": round(float(away_win_prob), 4)
            },
            "home_win_prob": round(float(home_win_prob), 4),
            "draw_prob": round(float(draw_prob), 4),
            "away_win_prob": round(float(away_win_prob), 4),
            "predicted_home_score": round(float(home_expected), 2),
            "predicted_away_score": round(float(away_expected), 2),
            "most_likely_score": most_likely_score,
            "model_details": {
                "model": self.model_name,
                "home_expected_goals": round(float(home_expected), 2),
                "away_expected_goals": round(float(away_expected), 2)
            }
        }

        if additional_details:
            response["model_details"].update(additional_details)

        return response

    def _calculate_outcome_probs_from_matrix(
        self,
        prob_matrix: np.ndarray
    ) -> tuple[float, float, float]:
        """
        Calculate W/D/L probabilities from scoreline probability matrix.

        Args:
            prob_matrix: Matrix where prob_matrix[h, a] = P(h home goals, a away goals)

        Returns:
            Tuple of (home_win_prob, draw_prob, away_win_prob)
        """
        home_win_prob = np.sum(np.tril(prob_matrix, -1))  # Home scores more
        draw_prob = np.sum(np.diag(prob_matrix))  # Equal scores
        away_win_prob = np.sum(np.triu(prob_matrix, 1))  # Away scores more

        return home_win_prob, draw_prob, away_win_prob

    def _find_most_likely_score(self, prob_matrix: np.ndarray) -> str:
        """
        Find the most likely scoreline from probability matrix.

        Args:
            prob_matrix: Scoreline probability matrix

        Returns:
            Most likely score as string (e.g., "2-1")
        """
        most_likely_idx = np.unravel_index(prob_matrix.argmax(), prob_matrix.shape)
        return f"{most_likely_idx[0]}-{most_likely_idx[1]}"


class BaseScorelineModel(BaseStatisticalModel):
    """
    Base class for models that predict full scoreline distributions.

    Examples: Poisson, Dixon-Coles, Bivariate Poisson, Zero-Inflated Poisson
    """

    def __init__(self, model_name: str, max_goals: int = 8):
        """
        Initialize scoreline model.

        Args:
            model_name: Name of the model
            max_goals: Maximum number of goals to consider in probability matrix
        """
        super().__init__(model_name)
        self.max_goals = max_goals

    def get_score_probabilities(
        self,
        prob_matrix: np.ndarray,
        top_n: int = 10
    ) -> list[Dict[str, Any]]:
        """
        Get top N most likely scorelines with their probabilities.

        Args:
            prob_matrix: Scoreline probability matrix
            top_n: Number of top scores to return

        Returns:
            List of dictionaries with 'score' and 'probability'
        """
        scores = []
        flat_indices = np.argsort(prob_matrix.flatten())[::-1][:top_n]

        for idx in flat_indices:
            h_goals, a_goals = np.unravel_index(idx, prob_matrix.shape)
            scores.append({
                "score": f"{h_goals}-{a_goals}",
                "probability": round(float(prob_matrix[h_goals, a_goals]), 4)
            })

        return scores


class BaseTotalsModel(BaseStatisticalModel):
    """
    Base class for models that predict total goals/cards/corners.

    Examples: Negative Binomial, Zero-Inflated Poisson
    """

    def __init__(self, model_name: str):
        super().__init__(model_name)

    @abstractmethod
    def predict_totals(
        self,
        home_attack: float,
        home_defense: float,
        away_attack: float,
        away_defense: float
    ) -> Dict[str, Any]:
        """
        Predict total goals distribution.

        Returns:
            Dictionary with:
                - expected_total: Expected total goals
                - over_under_probs: Dict of over/under probabilities for various lines
                - distribution: PMF of total goals
        """
        pass
