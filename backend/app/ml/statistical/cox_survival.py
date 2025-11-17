"""
Cox Proportional Hazards Model for Goal Timing Prediction

Models the hazard rate (instantaneous probability) of the next goal.
Useful for in-play predictions and understanding goal timing patterns.
"""

import numpy as np
from typing import Dict, Optional, List
from .base_statistical import BaseStatisticalModel


class CoxSurvivalModel(BaseStatisticalModel):
    """
    Cox Proportional Hazards model for football goal timing.

    Models when goals occur rather than just how many.
    The hazard function h(t) represents the instantaneous rate
    of scoring a goal at time t, given no goal up to time t.

    Best for:
    - In-play betting (live match predictions)
    - Next goal timing
    - Probability of goal in next N minutes
    - Late goal probabilities
    """

    def __init__(self, baseline_hazard: float = 0.03):
        """
        Initialize Cox Survival model.

        Args:
            baseline_hazard: Baseline hazard rate per minute (default ~0.03)
                           This means ~3% chance of goal each minute
        """
        super().__init__("cox_survival")
        self.baseline_hazard = baseline_hazard
        self.match_duration = 90  # Standard match length

    def predict(
        self,
        home_attack: float,
        home_defense: float,
        away_attack: float,
        away_defense: float,
        home_advantage: Optional[float] = None,
        current_time: int = 0
    ) -> Dict:
        """
        Predict match outcome incorporating survival analysis.

        Args:
            current_time: Current minute of the match (0-90+)

        Returns standard prediction dict plus survival-specific metrics.
        """
        if home_advantage is None:
            home_advantage = self.home_advantage

        # Calculate expected goals per minute
        lambda_home = home_attack * away_defense * home_advantage
        lambda_away = away_attack * home_defense

        # Convert to hazard rates
        hazard_home = self._goals_to_hazard(lambda_home)
        hazard_away = self._goals_to_hazard(lambda_away)

        # Predict expected goals in remaining time
        remaining_time = max(self.match_duration - current_time, 0)

        expected_home_remaining = hazard_home * remaining_time
        expected_away_remaining = hazard_away * remaining_time

        # Probability of goal in next N minutes
        next_goal_probs = {}
        for minutes in [5, 10, 15, 30]:
            prob_home_goal = self._prob_goal_in_period(hazard_home, minutes)
            prob_away_goal = self._prob_goal_in_period(hazard_away, minutes)
            prob_any_goal = 1 - (1 - prob_home_goal) * (1 - prob_away_goal)

            next_goal_probs[f"next_{minutes}_min"] = {
                "any_goal": round(prob_any_goal, 4),
                "home_goal": round(prob_home_goal, 4),
                "away_goal": round(prob_away_goal, 4)
            }

        # Simulate final score based on remaining time
        final_home = self._simulate_goals(hazard_home, remaining_time)
        final_away = self._simulate_goals(hazard_away, remaining_time)

        # Calculate win/draw/loss probabilities
        n_sims = 10000
        outcomes = self._simulate_outcomes(
            hazard_home, hazard_away, remaining_time, n_sims
        )

        home_win_prob = outcomes["home_wins"] / n_sims
        draw_prob = outcomes["draws"] / n_sims
        away_win_prob = outcomes["away_wins"] / n_sims

        most_likely_score = f"{final_home}-{final_away}"

        return self._standard_response(
            home_win_prob=home_win_prob,
            draw_prob=draw_prob,
            away_win_prob=away_win_prob,
            home_expected=expected_home_remaining,
            away_expected=expected_away_remaining,
            most_likely_score=most_likely_score,
            additional_details={
                "current_minute": current_time,
                "remaining_minutes": remaining_time,
                "hazard_rate_home": round(hazard_home, 4),
                "hazard_rate_away": round(hazard_away, 4),
                "next_goal_probabilities": next_goal_probs,
                "baseline_hazard": self.baseline_hazard
            }
        )

    def predict_next_goal_time(
        self,
        hazard_rate: float,
        current_time: int = 0
    ) -> Dict[str, float]:
        """
        Predict when the next goal will occur.

        Args:
            hazard_rate: Hazard rate (goals per minute)
            current_time: Current match time

        Returns:
            Dictionary with timing probabilities
        """
        # Survival function: S(t) = P(no goal until time t) = exp(-hazard * t)
        # Probability of goal in interval [t, t+Δt]

        time_intervals = [
            (0, 15),   # 0-15 min
            (15, 30),  # 15-30 min
            (30, 45),  # 30-45 min (+ stoppage)
            (45, 60),  # 45-60 min
            (60, 75),  # 60-75 min
            (75, 90)   # 75-90 min (+ stoppage)
        ]

        interval_probs = {}
        for start, end in time_intervals:
            if start >= current_time:
                # P(goal in [start, end] | survived until start)
                prob = self._prob_goal_in_interval(hazard_rate, start, end, current_time)
                interval_probs[f"{start}-{end}_min"] = round(prob, 4)

        # Expected time until next goal (exponential distribution)
        expected_time_to_goal = 1 / hazard_rate if hazard_rate > 0 else float('inf')

        return {
            "expected_minutes_to_goal": round(expected_time_to_goal, 2),
            "interval_probabilities": interval_probs
        }

    def _goals_to_hazard(self, expected_goals: float) -> float:
        """
        Convert expected goals (per match) to hazard rate (per minute).

        Hazard rate λ such that E[goals] = λ * match_duration
        """
        return expected_goals / self.match_duration

    def _prob_goal_in_period(self, hazard: float, minutes: int) -> float:
        """
        Probability of at least one goal in given period.

        P(goal in [0, t]) = 1 - S(t) = 1 - exp(-hazard * t)
        """
        return 1 - np.exp(-hazard * minutes)

    def _prob_goal_in_interval(
        self,
        hazard: float,
        start: int,
        end: int,
        current_time: int
    ) -> float:
        """
        Probability of goal in [start, end] given survival until current_time.

        P(goal in [start, end] | survived until current_time)
        """
        if start < current_time:
            start = current_time

        if start >= end:
            return 0.0

        # P(goal in [start, end]) = S(start) - S(end) = exp(-h*start) - exp(-h*end)
        # Conditional on survival until current_time: divide by S(current_time)

        prob_survive_to_start = np.exp(-hazard * (start - current_time))
        prob_survive_to_end = np.exp(-hazard * (end - current_time))

        return prob_survive_to_start - prob_survive_to_end

    def _simulate_goals(self, hazard: float, time_remaining: float) -> int:
        """
        Simulate number of goals in remaining time using Poisson process.
        """
        expected = hazard * time_remaining
        return int(np.round(expected))

    def _simulate_outcomes(
        self,
        hazard_home: float,
        hazard_away: float,
        time_remaining: float,
        n_sims: int = 10000
    ) -> Dict[str, int]:
        """
        Monte Carlo simulation of match outcomes.
        """
        np.random.seed(42)

        # Simulate goals as Poisson process
        lambda_home = hazard_home * time_remaining
        lambda_away = hazard_away * time_remaining

        home_goals = np.random.poisson(lambda_home, n_sims)
        away_goals = np.random.poisson(lambda_away, n_sims)

        home_wins = np.sum(home_goals > away_goals)
        draws = np.sum(home_goals == away_goals)
        away_wins = np.sum(home_goals < away_goals)

        return {
            "home_wins": int(home_wins),
            "draws": int(draws),
            "away_wins": int(away_wins)
        }


# Global instance
cox_survival_model = CoxSurvivalModel()
