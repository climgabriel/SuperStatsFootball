"""
Negative Binomial Model for Total Goals Prediction

Handles overdispersion in goal scoring (variance > mean).
Better than Poisson for teams with inconsistent scoring patterns.
"""

import numpy as np
from scipy.stats import nbinom
from typing import Dict, Optional
from .base_statistical import BaseTotalsModel


class NegativeBinomialModel(BaseTotalsModel):
    """
    Negative Binomial model for total goals prediction.

    The Negative Binomial distribution generalizes Poisson by allowing
    variance to exceed the mean, which is common in football where
    some teams have highly variable scoring rates.

    Best for:
    - Over/Under totals predictions
    - Teams with inconsistent scoring
    - Matches with high variance
    """

    def __init__(self, dispersion: float = 1.5):
        """
        Initialize Negative Binomial model.

        Args:
            dispersion: Overdispersion parameter (α)
                       Higher values = more variance
                       dispersion = 1 means Var = Mean (Poisson-like)
                       dispersion > 1 means Var > Mean (overdispersed)
        """
        super().__init__("negative_binomial")
        self.dispersion = dispersion

    def predict(
        self,
        home_attack: float,
        home_defense: float,
        away_attack: float,
        away_defense: float,
        home_advantage: Optional[float] = None
    ) -> Dict:
        """
        Predict match outcome using Negative Binomial for goal totals.
        """
        if home_advantage is None:
            home_advantage = self.home_advantage

        # Calculate expected goals
        lambda_home = home_attack * away_defense * home_advantage
        lambda_away = away_attack * home_defense

        # Total expected goals
        total_expected = lambda_home + lambda_away

        # Convert to Negative Binomial parameters
        # NegBin parameterized by (n, p) where:
        # E[X] = n(1-p)/p = μ
        # Var[X] = n(1-p)/p² = μ + α*μ² (with dispersion α)

        n, p = self._convert_to_nbinom_params(total_expected, self.dispersion)

        # Calculate over/under probabilities
        over_under_probs = {}
        for line in [0.5, 1.5, 2.5, 3.5, 4.5, 5.5]:
            # P(Total > line)
            over_prob = 1 - nbinom.cdf(line, n, p)
            under_prob = nbinom.cdf(line, n, p)

            over_under_probs[f"over_{line}"] = round(float(over_prob), 4)
            over_under_probs[f"under_{line}"] = round(float(under_prob), 4)

        # Most likely total goals
        mode = int(nbinom.mode(n, p)) if n > 1 else int(round(total_expected))

        # Estimate scoreline from totals (simplified)
        # Use ratio of home/away expected goals
        home_ratio = lambda_home / total_expected if total_expected > 0 else 0.5

        # For win/draw/loss, we need individual goal distributions
        n_home, p_home = self._convert_to_nbinom_params(lambda_home, self.dispersion)
        n_away, p_away = self._convert_to_nbinom_params(lambda_away, self.dispersion)

        # Approximate outcome probabilities by simulating
        home_win_prob, draw_prob, away_win_prob = self._simulate_outcomes(
            n_home, p_home, n_away, p_away, n_sims=10000
        )

        # Most likely scoreline (crude approximation)
        home_mode = int(nbinom.mode(n_home, p_home)) if n_home > 1 else int(round(lambda_home))
        away_mode = int(nbinom.mode(n_away, p_away)) if n_away > 1 else int(round(lambda_away))
        most_likely_score = f"{home_mode}-{away_mode}"

        return self._standard_response(
            home_win_prob=home_win_prob,
            draw_prob=draw_prob,
            away_win_prob=away_win_prob,
            home_expected=lambda_home,
            away_expected=lambda_away,
            most_likely_score=most_likely_score,
            additional_details={
                "total_expected_goals": round(total_expected, 2),
                "most_likely_total": mode,
                "over_under_probabilities": over_under_probs,
                "dispersion_parameter": self.dispersion,
                "variance": round(total_expected * (1 + self.dispersion * total_expected), 2)
            }
        )

    def predict_totals(
        self,
        home_attack: float,
        home_defense: float,
        away_attack: float,
        away_defense: float
    ) -> Dict:
        """
        Predict total goals distribution (specialized method).

        Returns detailed totals probabilities.
        """
        lambda_home = home_attack * away_defense * self.home_advantage
        lambda_away = away_attack * home_defense
        total_expected = lambda_home + lambda_away

        n, p = self._convert_to_nbinom_params(total_expected, self.dispersion)

        # Calculate PMF for total goals
        max_goals = 15
        totals_pmf = {}
        for k in range(max_goals):
            totals_pmf[k] = round(float(nbinom.pmf(k, n, p)), 4)

        # Over/under for common lines
        over_under = {}
        for line in [0.5, 1.5, 2.5, 3.5, 4.5, 5.5]:
            over_under[line] = {
                "over": round(float(1 - nbinom.cdf(line, n, p)), 4),
                "under": round(float(nbinom.cdf(line, n, p)), 4)
            }

        return {
            "expected_total": round(total_expected, 2),
            "variance": round(total_expected * (1 + self.dispersion * total_expected), 2),
            "most_likely_total": int(nbinom.mode(n, p)) if n > 1 else int(round(total_expected)),
            "totals_pmf": totals_pmf,
            "over_under_lines": over_under,
            "dispersion": self.dispersion
        }

    def _convert_to_nbinom_params(self, mu: float, alpha: float) -> tuple[float, float]:
        """
        Convert (mean, dispersion) to NegBin(n, p) parameters.

        For NegBin(n, p): E[X] = n(1-p)/p, Var[X] = n(1-p)/p²
        With overdispersion: Var = μ + α*μ²

        Solving: n = μ²/(Var - μ) = μ/α, p = μ/(μ + α*μ²) = 1/(1 + α*μ)
        """
        if mu <= 0:
            return 1.0, 0.5

        n = mu / alpha if alpha > 0 else mu
        p = 1 / (1 + alpha * mu) if alpha > 0 else 0.5

        # Ensure valid parameters
        n = max(n, 0.1)
        p = max(min(p, 0.999), 0.001)

        return n, p

    def _simulate_outcomes(
        self,
        n_home: float,
        p_home: float,
        n_away: float,
        p_away: float,
        n_sims: int = 10000
    ) -> tuple[float, float, float]:
        """
        Simulate match outcomes using Negative Binomial distributions.
        """
        np.random.seed(42)  # For reproducibility

        home_goals = nbinom.rvs(n_home, p_home, size=n_sims)
        away_goals = nbinom.rvs(n_away, p_away, size=n_sims)

        home_wins = np.sum(home_goals > away_goals) / n_sims
        draws = np.sum(home_goals == away_goals) / n_sims
        away_wins = np.sum(home_goals < away_goals) / n_sims

        return home_wins, draws, away_wins


# Global instance
negative_binomial_model = NegativeBinomialModel()
