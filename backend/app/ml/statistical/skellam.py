"""
Skellam Distribution Model for Football Outcome Prediction

Models the goal difference distribution to predict match outcomes.
The Skellam distribution is the distribution of the difference between
two independent Poisson random variables.
"""

import numpy as np
from scipy.stats import skellam, poisson
from typing import Dict, Optional
from .base_statistical import BaseStatisticalModel


class SkellamModel(BaseStatisticalModel):
    """
    Skellam model for football match outcome prediction.

    The Skellam distribution models D = X - Y where:
    - X ~ Poisson(λ_home)  # Home goals
    - Y ~ Poisson(λ_away)  # Away goals
    - D ~ Skellam(λ_home, λ_away)  # Goal difference

    Best for:
    - Win/Draw/Loss predictions
    - Handicap betting markets
    - Goal difference analysis
    """

    def __init__(self):
        super().__init__("skellam")

    def predict(
        self,
        home_attack: float,
        home_defense: float,
        away_attack: float,
        away_defense: float,
        home_advantage: Optional[float] = None
    ) -> Dict:
        """
        Predict match outcome using Skellam distribution.

        Returns probabilities for:
        - Home win (D > 0)
        - Draw (D = 0)
        - Away win (D < 0)
        """
        if home_advantage is None:
            home_advantage = self.home_advantage

        # Calculate expected goals
        lambda_home = home_attack * away_defense * home_advantage
        lambda_away = away_attack * home_defense

        # Calculate outcome probabilities from Skellam distribution
        # D ranges from -max_diff to +max_diff
        max_diff = 10
        goal_diffs = np.arange(-max_diff, max_diff + 1)

        # PMF of goal difference
        diff_pmf = skellam.pmf(goal_diffs, lambda_home, lambda_away)

        # Calculate outcome probabilities
        draw_prob = float(skellam.pmf(0, lambda_home, lambda_away))
        home_win_prob = float(np.sum(diff_pmf[goal_diffs > 0]))
        away_win_prob = float(np.sum(diff_pmf[goal_diffs < 0]))

        # Normalize (should already sum to ~1, but ensure)
        total = home_win_prob + draw_prob + away_win_prob
        home_win_prob /= total
        draw_prob /= total
        away_win_prob /= total

        # Most likely goal difference
        most_likely_diff = goal_diffs[np.argmax(diff_pmf)]

        # Estimate most likely score based on expected goals and most likely difference
        # If diff is positive, home likely to win by that margin
        if most_likely_diff > 0:
            # Home wins
            home_score = int(round(lambda_home))
            away_score = max(0, home_score - most_likely_diff)
        elif most_likely_diff < 0:
            # Away wins
            away_score = int(round(lambda_away))
            home_score = max(0, away_score + most_likely_diff)
        else:
            # Draw
            avg_goals = (lambda_home + lambda_away) / 2
            home_score = int(round(avg_goals))
            away_score = home_score

        most_likely_score = f"{home_score}-{away_score}"

        # Calculate handicap probabilities (useful for betting)
        handicap_probs = {}
        for handicap in [-2, -1, 0, 1, 2]:
            # P(home wins with handicap)
            handicap_probs[f"home_{handicap:+d}"] = float(
                np.sum(diff_pmf[goal_diffs > -handicap])
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
                "expected_goal_difference": round(lambda_home - lambda_away, 2),
                "most_likely_goal_difference": int(most_likely_diff),
                "handicap_probabilities": handicap_probs
            }
        )

    def predict_goal_difference_distribution(
        self,
        lambda_home: float,
        lambda_away: float,
        max_diff: int = 10
    ) -> Dict[int, float]:
        """
        Get full goal difference distribution.

        Args:
            lambda_home: Expected home goals
            lambda_away: Expected away goals
            max_diff: Maximum goal difference to consider

        Returns:
            Dictionary mapping goal difference to probability
        """
        goal_diffs = np.arange(-max_diff, max_diff + 1)
        probs = skellam.pmf(goal_diffs, lambda_home, lambda_away)

        return {int(diff): float(prob) for diff, prob in zip(goal_diffs, probs)}


# Global instance
skellam_model = SkellamModel()
