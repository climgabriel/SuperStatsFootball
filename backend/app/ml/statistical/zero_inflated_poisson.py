"""
Zero-Inflated Poisson Model for Football Prediction

Handles excess zero scores (0-0, 0-1, 1-0) which are common in football.
Mixes Poisson distribution with extra probability mass at zero.
"""

import numpy as np
from scipy.stats import poisson
from typing import Dict, Optional
from .base_statistical import BaseScorelineModel


class ZeroInflatedPoissonModel(BaseScorelineModel):
    """
    Zero-Inflated Poisson (ZIP) model for football predictions.

    The ZIP model is a mixture of:
    - A point mass at zero (probability π)
    - A Poisson distribution (probability 1-π)

    This accounts for matches where "nothing happens" (defensive,
    cautious play, bad conditions, etc.) leading to more 0-0, 0-1, 1-0
    scorelines than Poisson predicts.

    Best for:
    - Defensive teams
    - Derby matches (tight, cautious)
    - Bad weather conditions
    - Knockout matches
    """

    def __init__(self, pi_home: float = 0.15, pi_away: float = 0.15):
        """
        Initialize Zero-Inflated Poisson model.

        Args:
            pi_home: Excess zero probability for home goals (0.0-0.3 typical)
            pi_away: Excess zero probability for away goals (0.0-0.3 typical)
        """
        super().__init__("zero_inflated_poisson")
        self.pi_home = pi_home  # Probability of structural zero (home)
        self.pi_away = pi_away  # Probability of structural zero (away)

    def predict(
        self,
        home_attack: float,
        home_defense: float,
        away_attack: float,
        away_defense: float,
        home_advantage: Optional[float] = None
    ) -> Dict:
        """
        Predict match outcome using Zero-Inflated Poisson model.

        For each team:
        P(X = 0) = π + (1-π) * Poisson(0; λ) = π + (1-π) * exp(-λ)
        P(X = k) = (1-π) * Poisson(k; λ) for k > 0
        """
        if home_advantage is None:
            home_advantage = self.home_advantage

        # Calculate expected goals
        lambda_home = home_attack * away_defense * home_advantage
        lambda_away = away_attack * home_defense

        # Calculate scoreline probabilities using ZIP
        prob_matrix = self._calculate_zip_pmf(lambda_home, lambda_away)

        # Normalize probabilities
        prob_matrix /= prob_matrix.sum()

        # Calculate outcome probabilities
        home_win_prob, draw_prob, away_win_prob = \
            self._calculate_outcome_probs_from_matrix(prob_matrix)

        # Find most likely score
        most_likely_score = self._find_most_likely_score(prob_matrix)

        # Get top scorelines
        top_scores = self.get_score_probabilities(prob_matrix, top_n=5)

        # Calculate probability of 0-0 specifically (often elevated with ZIP)
        prob_0_0 = float(prob_matrix[0, 0])

        # Calculate probability of "boring" match (total goals <= 1)
        prob_low_scoring = float(
            prob_matrix[0, 0] + prob_matrix[0, 1] + prob_matrix[1, 0]
        )

        return self._standard_response(
            home_win_prob=home_win_prob,
            draw_prob=draw_prob,
            away_win_prob=away_win_prob,
            home_expected=lambda_home,
            away_expected=lambda_away,
            most_likely_score=most_likely_score,
            additional_details={
                "lambda_home": round(lambda_home, 2),
                "lambda_away": round(lambda_away, 2),
                "pi_home": round(self.pi_home, 3),
                "pi_away": round(self.pi_away, 3),
                "prob_0_0": round(prob_0_0, 4),
                "prob_low_scoring": round(prob_low_scoring, 4),
                "top_scores": top_scores
            }
        )

    def _calculate_zip_pmf(
        self,
        lambda_home: float,
        lambda_away: float
    ) -> np.ndarray:
        """
        Calculate Zero-Inflated Poisson PMF for scorelines.

        P(H=h, A=a) = P_ZIP(H=h) * P_ZIP(A=a)

        where P_ZIP(X=k) = π*I(k=0) + (1-π)*Poisson(k; λ)
        """
        prob_matrix = np.zeros((self.max_goals, self.max_goals))

        # Calculate ZIP probabilities for each goal count
        home_probs = self._zip_pmf(lambda_home, self.pi_home, self.max_goals)
        away_probs = self._zip_pmf(lambda_away, self.pi_away, self.max_goals)

        # Outer product for joint probability (assuming independence)
        prob_matrix = np.outer(home_probs, away_probs)

        return prob_matrix

    def _zip_pmf(self, lambda_: float, pi: float, max_goals: int) -> np.ndarray:
        """
        Calculate ZIP PMF for goal counts 0 to max_goals-1.

        P(X = 0) = π + (1-π) * exp(-λ)
        P(X = k) = (1-π) * Poisson(k; λ) for k > 0
        """
        probs = np.zeros(max_goals)

        # Zero goals (inflated)
        probs[0] = pi + (1 - pi) * poisson.pmf(0, lambda_)

        # Non-zero goals
        for k in range(1, max_goals):
            probs[k] = (1 - pi) * poisson.pmf(k, lambda_)

        return probs

    def estimate_zero_inflation(
        self,
        goals: np.ndarray
    ) -> float:
        """
        Estimate zero-inflation parameter π from goal data.

        Uses method of moments: observed zeros vs expected zeros under Poisson.

        Args:
            goals: Array of goal counts

        Returns:
            Estimated π (excess zero probability)
        """
        if len(goals) == 0:
            return 0.15  # Default

        # Observed proportion of zeros
        n_zeros = np.sum(goals == 0)
        obs_zero_prop = n_zeros / len(goals)

        # Expected proportion under Poisson
        lambda_hat = np.mean(goals)
        exp_zero_prop = np.exp(-lambda_hat)

        # Estimate π
        if obs_zero_prop > exp_zero_prop:
            pi = (obs_zero_prop - exp_zero_prop) / (1 - exp_zero_prop)
            return min(max(pi, 0.0), 0.5)  # Clamp to [0, 0.5]
        else:
            return 0.0  # No zero inflation detected


# Global instance
zero_inflated_poisson_model = ZeroInflatedPoissonModel()
