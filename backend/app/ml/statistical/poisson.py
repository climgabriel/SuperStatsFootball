"""
Poisson Distribution Model for Football Match Prediction

Based on the Poisson distribution to model goal scoring probabilities.
"""

import numpy as np
from scipy.stats import poisson
from typing import Dict, Tuple


class PoissonModel:
    """
    Poisson model for predicting football match outcomes.

    Assumes goals scored by each team follow a Poisson distribution.
    """

    def __init__(self):
        self.home_advantage = 1.3  # Default home advantage factor

    def predict(
        self,
        home_attack: float,
        home_defense: float,
        away_attack: float,
        away_defense: float,
        home_advantage: float = None
    ) -> Dict:
        """
        Predict match outcome using Poisson distribution.

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

        # Calculate expected goals
        home_expected = home_attack * away_defense * home_advantage
        away_expected = away_attack * home_defense

        # Calculate probabilities for each score
        max_goals = 8  # Maximum goals to consider
        prob_matrix = np.zeros((max_goals, max_goals))

        for home_goals in range(max_goals):
            for away_goals in range(max_goals):
                prob_matrix[home_goals, away_goals] = (
                    poisson.pmf(home_goals, home_expected) *
                    poisson.pmf(away_goals, away_expected)
                )

        # Calculate outcome probabilities
        home_win_prob = np.sum(np.tril(prob_matrix, -1))  # Home scores more
        draw_prob = np.sum(np.diag(prob_matrix))  # Equal scores
        away_win_prob = np.sum(np.triu(prob_matrix, 1))  # Away scores more

        # Normalize probabilities
        total_prob = home_win_prob + draw_prob + away_win_prob
        home_win_prob /= total_prob
        draw_prob /= total_prob
        away_win_prob /= total_prob

        # Find most likely score
        most_likely_idx = np.unravel_index(prob_matrix.argmax(), prob_matrix.shape)
        most_likely_score = f"{most_likely_idx[0]}-{most_likely_idx[1]}"

        return {
            "probabilities": {
                "home_win": round(home_win_prob, 4),
                "draw": round(draw_prob, 4),
                "away_win": round(away_win_prob, 4)
            },
            "home_win_prob": round(home_win_prob, 4),
            "draw_prob": round(draw_prob, 4),
            "away_win_prob": round(away_win_prob, 4),
            "predicted_home_score": round(home_expected, 2),
            "predicted_away_score": round(away_expected, 2),
            "most_likely_score": most_likely_score,
            "model_details": {
                "model": "poisson",
                "home_expected_goals": round(home_expected, 2),
                "away_expected_goals": round(away_expected, 2)
            }
        }

    def calculate_team_strengths(self, goals_scored: int, goals_conceded: int, matches_played: int) -> Tuple[float, float]:
        """
        Calculate team's attacking and defensive strengths.

        Args:
            goals_scored: Total goals scored
            goals_conceded: Total goals conceded
            matches_played: Number of matches played

        Returns:
            Tuple of (attack_strength, defense_strength)
        """
        league_avg_goals = 1.4  # Average goals per team per match

        attack_strength = (goals_scored / matches_played) / league_avg_goals if matches_played > 0 else 1.0
        defense_strength = (goals_conceded / matches_played) / league_avg_goals if matches_played > 0 else 1.0

        return attack_strength, defense_strength


# Global instance
poisson_model = PoissonModel()
