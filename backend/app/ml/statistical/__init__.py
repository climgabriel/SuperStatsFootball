"""Statistical models for football prediction."""

from .poisson import PoissonModel, poisson_model
from .dixon_coles import DixonColesModel, dixon_coles_model
from .elo import EloModel, elo_model
from .bivariate_poisson import BivariatePoissonModel, bivariate_poisson_model
from .skellam import SkellamModel, skellam_model
from .negative_binomial import NegativeBinomialModel, negative_binomial_model
from .zero_inflated_poisson import ZeroInflatedPoissonModel, zero_inflated_poisson_model
from .cox_survival import CoxSurvivalModel, cox_survival_model

__all__ = [
    # Classes
    "PoissonModel",
    "DixonColesModel",
    "EloModel",
    "BivariatePoissonModel",
    "SkellamModel",
    "NegativeBinomialModel",
    "ZeroInflatedPoissonModel",
    "CoxSurvivalModel",
    # Instances
    "poisson_model",
    "dixon_coles_model",
    "elo_model",
    "bivariate_poisson_model",
    "skellam_model",
    "negative_binomial_model",
    "zero_inflated_poisson_model",
    "cox_survival_model",
]
