"""
Elo Rating System for Football Teams

Adapts chess Elo rating for football predictions.
"""

import math
from typing import Dict, Tuple


class EloModel:
    """
    Elo rating system for football teams.

    Higher rating indicates stronger team.
    """

    def __init__(self, k_factor: float = 40.0, home_advantage: float = 100.0):
        """
        Initialize Elo model.

        Args:
            k_factor: K-factor for rating updates (higher = more volatile)
            home_advantage: Rating boost for home team
        """
        self.k_factor = k_factor
        self.home_advantage = home_advantage
        self.default_rating = 1500.0

    def predict(self, home_rating: float, away_rating: float) -> Dict:
        """
        Predict match outcome based on Elo ratings.

        Args:
            home_rating: Home team's Elo rating
            away_rating: Away team's Elo rating

        Returns:
            Dictionary containing prediction probabilities
        """
        # Adjust for home advantage
        adjusted_home_rating = home_rating + self.home_advantage

        # Calculate expected scores using Elo formula
        home_expected = self._expected_score(adjusted_home_rating, away_rating)
        away_expected = 1 - home_expected

        # Convert to win/draw/loss probabilities
        # Using empirical football-specific conversion
        draw_prob = 0.25  # Base draw probability

        # Adjust based on rating difference
        rating_diff = adjusted_home_rating - away_rating
        draw_factor = max(0.15, 0.30 - abs(rating_diff) / 1000)

        home_win_prob = home_expected * (1 - draw_factor)
        away_win_prob = away_expected * (1 - draw_factor)
        draw_prob = draw_factor

        # Normalize
        total = home_win_prob + draw_prob + away_win_prob
        home_win_prob /= total
        draw_prob /= total
        away_win_prob /= total

        # Estimate expected goals based on rating
        home_expected_goals = 1.0 + (home_rating - 1500) / 300
        away_expected_goals = 1.0 + (away_rating - 1500) / 300

        return {
            "home_win_prob": round(home_win_prob, 4),
            "draw_prob": round(draw_prob, 4),
            "away_win_prob": round(away_win_prob, 4),
            "predicted_home_score": round(max(0, home_expected_goals), 2),
            "predicted_away_score": round(max(0, away_expected_goals), 2),
            "model_details": {
                "model": "elo",
                "home_rating": home_rating,
                "away_rating": away_rating,
                "rating_difference": round(rating_diff, 2)
            }
        }

    def update_ratings(
        self,
        home_rating: float,
        away_rating: float,
        home_goals: int,
        away_goals: int
    ) -> Tuple[float, float]:
        """
        Update Elo ratings after a match.

        Args:
            home_rating: Home team's current rating
            away_rating: Away team's current rating
            home_goals: Goals scored by home team
            away_goals: Goals scored by away team

        Returns:
            Tuple of (new_home_rating, new_away_rating)
        """
        # Adjust for home advantage
        adjusted_home_rating = home_rating + self.home_advantage

        # Expected scores
        home_expected = self._expected_score(adjusted_home_rating, away_rating)
        away_expected = 1 - home_expected

        # Actual scores (1 for win, 0.5 for draw, 0 for loss)
        if home_goals > away_goals:
            home_actual = 1.0
            away_actual = 0.0
        elif home_goals < away_goals:
            home_actual = 0.0
            away_actual = 1.0
        else:
            home_actual = 0.5
            away_actual = 0.5

        # Goal difference multiplier (larger wins = bigger rating change)
        goal_diff = abs(home_goals - away_goals)
        multiplier = math.log(max(goal_diff, 1) + 1)

        # Update ratings
        new_home_rating = home_rating + self.k_factor * multiplier * (home_actual - home_expected)
        new_away_rating = away_rating + self.k_factor * multiplier * (away_actual - away_expected)

        return round(new_home_rating, 2), round(new_away_rating, 2)

    def _expected_score(self, rating_a: float, rating_b: float) -> float:
        """
        Calculate expected score for team A vs team B.

        Returns value between 0 and 1.
        """
        return 1 / (1 + math.pow(10, (rating_b - rating_a) / 400))


# Global instance
elo_model = EloModel()
