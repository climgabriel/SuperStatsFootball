"""
Dixon-Coles Model for Football Match Prediction

Extension of Poisson model with correlation between home and away goals,
particularly for low-scoring outcomes.
"""

import numpy as np
from scipy.stats import poisson
from typing import Dict


class DixonColesModel:
    """
    Dixon-Coles model for predicting football match outcomes.

    Improves on basic Poisson by accounting for correlation in low-scoring games.
    """

    def __init__(self, rho: float = -0.13):
        """
        Initialize Dixon-Coles model.

        Args:
            rho: Correlation parameter (typically negative, around -0.13)
        """
        self.rho = rho
        self.home_advantage = 1.3

    def tau(self, home_goals: int, away_goals: int, lambda_home: float, lambda_away: float) -> float:
        """
        Calculate tau adjustment factor for Dixon-Coles.

        Adjusts probabilities for low-scoring outcomes (0-0, 0-1, 1-0, 1-1).
        """
        if home_goals == 0 and away_goals == 0:
            return 1 - lambda_home * lambda_away * self.rho
        elif home_goals == 0 and away_goals == 1:
            return 1 + lambda_home * self.rho
        elif home_goals == 1 and away_goals == 0:
            return 1 + lambda_away * self.rho
        elif home_goals == 1 and away_goals == 1:
            return 1 - self.rho
        else:
            return 1.0

    def predict(
        self,
        home_attack: float,
        home_defense: float,
        away_attack: float,
        away_defense: float,
        home_advantage: float = None
    ) -> Dict:
        """
        Predict match outcome using Dixon-Coles model.

        Args:
            home_attack: Home team's attacking strength
            home_defense: Home team's defensive strength
            away_attack: Away team's attacking strength
            away_defense: Away team's defensive strength
            home_advantage: Home advantage factor (optional)

        Returns:
            Dictionary containing prediction probabilities and scores
        """
        if home_advantage is None:
            home_advantage = self.home_advantage

        # Calculate expected goals (lambdas)
        lambda_home = home_attack * away_defense * home_advantage
        lambda_away = away_attack * home_defense

        # Calculate probabilities for each score
        max_goals = 8
        prob_matrix = np.zeros((max_goals, max_goals))

        for home_goals in range(max_goals):
            for away_goals in range(max_goals):
                # Basic Poisson probability
                poisson_prob = (
                    poisson.pmf(home_goals, lambda_home) *
                    poisson.pmf(away_goals, lambda_away)
                )

                # Dixon-Coles adjustment
                tau_factor = self.tau(home_goals, away_goals, lambda_home, lambda_away)

                prob_matrix[home_goals, away_goals] = poisson_prob * tau_factor

        # Normalize probabilities
        prob_matrix /= prob_matrix.sum()

        # Calculate outcome probabilities
        home_win_prob = np.sum(np.tril(prob_matrix, -1))
        draw_prob = np.sum(np.diag(prob_matrix))
        away_win_prob = np.sum(np.triu(prob_matrix, 1))

        # Find most likely score
        most_likely_idx = np.unravel_index(prob_matrix.argmax(), prob_matrix.shape)
        most_likely_score = f"{most_likely_idx[0]}-{most_likely_idx[1]}"

        # Calculate score distribution for top outcomes
        score_probabilities = []
        flat_indices = np.argsort(prob_matrix.flatten())[::-1][:10]  # Top 10 scores
        for idx in flat_indices:
            h_goals, a_goals = np.unravel_index(idx, prob_matrix.shape)
            score_probabilities.append({
                "score": f"{h_goals}-{a_goals}",
                "probability": round(float(prob_matrix[h_goals, a_goals]), 4)
            })

        return {
            "home_win_prob": round(float(home_win_prob), 4),
            "draw_prob": round(float(draw_prob), 4),
            "away_win_prob": round(float(away_win_prob), 4),
            "predicted_home_score": round(float(lambda_home), 2),
            "predicted_away_score": round(float(lambda_away), 2),
            "most_likely_score": most_likely_score,
            "model_details": {
                "model": "dixon_coles",
                "lambda_home": round(float(lambda_home), 2),
                "lambda_away": round(float(lambda_away), 2),
                "rho": self.rho,
                "top_scores": score_probabilities[:5]
            }
        }


# Global instance
dixon_coles_model = DixonColesModel()
