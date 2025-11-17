"""
Bivariate Poisson Model for Football Match Prediction

Models home and away goals jointly with correlation parameter.
Improves on independent Poisson by accounting for covariance.
"""

import numpy as np
from scipy.stats import poisson
from typing import Dict, Optional
from .base_statistical import BaseScorelineModel


class BivariatePoissonModel(BaseScorelineModel):
    """
    Bivariate Poisson model for football predictions.

    Extends independent Poisson to include correlation between
    home and away goals. Particularly useful for:
    - Matches where both teams score frequently
    - Derby matches with unusual dynamics
    - Scoreline predictions with dependencies
    """

    def __init__(self, lambda_0: float = 0.1):
        """
        Initialize Bivariate Poisson model.

        Args:
            lambda_0: Correlation parameter (typically 0.05-0.15)
                     Positive values indicate positive correlation
        """
        super().__init__("bivariate_poisson")
        self.lambda_0 = lambda_0

    def predict(
        self,
        home_attack: float,
        home_defense: float,
        away_attack: float,
        away_defense: float,
        home_advantage: Optional[float] = None
    ) -> Dict:
        """
        Predict match outcome using Bivariate Poisson model.

        The model assumes:
        - Home goals ~ Poisson(λ₁ + λ₀)
        - Away goals ~ Poisson(λ₂ + λ₀)
        - Common component ~ Poisson(λ₀)

        This creates correlation while maintaining marginal Poisson distributions.
        """
        if home_advantage is None:
            home_advantage = self.home_advantage

        # Calculate marginal expected goals
        lambda_home = home_attack * away_defense * home_advantage
        lambda_away = away_attack * home_defense

        # Adjust for correlation
        # λ₁ = λ_home - λ₀, λ₂ = λ_away - λ₀
        lambda_1 = max(lambda_home - self.lambda_0, 0.01)
        lambda_2 = max(lambda_away - self.lambda_0, 0.01)

        # Calculate scoreline probabilities
        prob_matrix = self._calculate_bivariate_pmf(
            lambda_1, lambda_2, self.lambda_0
        )

        # Normalize probabilities
        prob_matrix /= prob_matrix.sum()

        # Calculate outcome probabilities
        home_win_prob, draw_prob, away_win_prob = \
            self._calculate_outcome_probs_from_matrix(prob_matrix)

        # Find most likely score
        most_likely_score = self._find_most_likely_score(prob_matrix)

        # Get top scorelines
        top_scores = self.get_score_probabilities(prob_matrix, top_n=5)

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
                "lambda_0": round(self.lambda_0, 3),
                "correlation": "positive" if self.lambda_0 > 0 else "negative",
                "top_scores": top_scores
            }
        )

    def _calculate_bivariate_pmf(
        self,
        lambda_1: float,
        lambda_2: float,
        lambda_0: float
    ) -> np.ndarray:
        """
        Calculate bivariate Poisson PMF.

        P(X₁=x, X₂=y) = P(W₁=x-k) * P(W₂=y-k) * P(W₀=k)
        where W₁ ~ Poisson(λ₁), W₂ ~ Poisson(λ₂), W₀ ~ Poisson(λ₀)
        and X₁ = W₁ + W₀, X₂ = W₂ + W₀
        """
        prob_matrix = np.zeros((self.max_goals, self.max_goals))

        for home_goals in range(self.max_goals):
            for away_goals in range(self.max_goals):
                prob = 0.0
                max_k = min(home_goals, away_goals) + 1

                for k in range(max_k):
                    # Probability from independent components
                    p_w1 = poisson.pmf(home_goals - k, lambda_1)
                    p_w2 = poisson.pmf(away_goals - k, lambda_2)
                    p_w0 = poisson.pmf(k, lambda_0)

                    prob += p_w1 * p_w2 * p_w0

                prob_matrix[home_goals, away_goals] = prob

        return prob_matrix

    def estimate_correlation(
        self,
        match_data: list,
        method: str = "moment"
    ) -> float:
        """
        Estimate correlation parameter from historical match data.

        Args:
            match_data: List of matches with home_goals and away_goals
            method: Estimation method ('moment' or 'mle')

        Returns:
            Estimated λ₀ parameter
        """
        if not match_data:
            return 0.1  # Default

        home_goals = np.array([m['home_goals'] for m in match_data])
        away_goals = np.array([m['away_goals'] for m in match_data])

        if method == "moment":
            # Method of moments estimator
            covariance = np.cov(home_goals, away_goals)[0, 1]
            # λ₀ = Cov(X, Y) for bivariate Poisson
            return max(0.0, covariance)
        else:
            # Use default for now (MLE is more complex)
            return 0.1


# Global instance
bivariate_poisson_model = BivariatePoissonModel()
