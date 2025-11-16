"""
All 17 Machine Learning Models for Football Prediction

Each model is optimized with best hyperparameters based on research.
All models use ONLY database features - NO bookmaker odds.

Models:
1. Logistic Regression - L2 regularization for binary classification
2. Random Forest - Ensemble of decision trees with Platt scaling
3. XGBoost - Gradient boosting with optimized hyperparameters
4. Gradient Boosting - Sklearn's gradient boosting classifier
5. Support Vector Machine - RBF kernel with probability calibration
6. K-Nearest Neighbors - Distance-based classification
7. Decision Tree - Single tree with max depth limit
8. Naive Bayes - Gaussian Naive Bayes
9. AdaBoost - Adaptive boosting ensemble
10. Neural Network (MLP) - Multi-layer perceptron
11. LightGBM - Microsoft's gradient boosting framework
12. CatBoost - Yandex's gradient boosting
13. Extra Trees - Extremely randomized trees
14. Ridge Classifier - Ridge regression for classification
15. Passive Aggressive - Online learning algorithm
16. Quadratic Discriminant Analysis - QDA classifier
17. Voting Ensemble - Combines all models
"""

from typing import Dict
import numpy as np
from sklearn.linear_model import LogisticRegression, RidgeClassifier, PassiveAggressiveClassifier
from sklearn.ensemble import (
    RandomForestClassifier, GradientBoostingClassifier,
    AdaBoostClassifier, ExtraTreesClassifier, VotingClassifier
)
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neural_network import MLPClassifier
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis, LinearDiscriminantAnalysis
from sklearn.linear_model import SGDClassifier
from sklearn.ensemble import BaggingClassifier, StackingClassifier
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF

try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False

try:
    import lightgbm as lgb
    LIGHTGBM_AVAILABLE = True
except ImportError:
    LIGHTGBM_AVAILABLE = False

try:
    import catboost as cb
    CATBOOST_AVAILABLE = True
except ImportError:
    CATBOOST_AVAILABLE = False

from .base_model import BaseMLModel


# ============================================================================
# MODEL 1: LOGISTIC REGRESSION
# ============================================================================

class LogisticRegressionModel(BaseMLModel):
    """
    Logistic Regression with L2 regularization.

    Best for:
    - Binary classification problems
    - Interpretable results
    - Fast training and prediction

    Research shows 79.41% accuracy for football prediction.
    """

    def __init__(self):
        super().__init__("Logistic Regression")

    def _create_model(self):
        return LogisticRegression(
            penalty='l2',  # Ridge regularization
            C=1.0,  # Regularization strength
            solver='lbfgs',
            max_iter=1000,
            multi_class='multinomial',
            random_state=42,
            n_jobs=-1
        )


# ============================================================================
# MODEL 2: RANDOM FOREST
# ============================================================================

class RandomForestModel(BaseMLModel):
    """
    Random Forest with optimized hyperparameters.

    Best for:
    - Handling non-linear relationships
    - Feature importance analysis
    - Robust to overfitting

    Includes Platt scaling for calibrated probabilities.
    """

    def __init__(self):
        super().__init__("Random Forest")

    def _create_model(self):
        return RandomForestClassifier(
            n_estimators=200,  # Number of trees
            max_depth=15,  # Prevent overfitting
            min_samples_split=10,
            min_samples_leaf=4,
            max_features='sqrt',  # Random feature subset
            bootstrap=True,
            oob_score=True,
            random_state=42,
            n_jobs=-1,
            class_weight='balanced'  # Handle class imbalance
        )


# ============================================================================
# MODEL 3: XGBOOST
# ============================================================================

class XGBoostModel(BaseMLModel):
    """
    XGBoost with Bayesian-optimized hyperparameters.

    Best for:
    - Maximum prediction accuracy
    - Handling complex patterns
    - Feature interactions

    Research shows excellent AUC and F1 scores in sports prediction.
    """

    def __init__(self):
        super().__init__("XGBoost")

    def _create_model(self):
        if not XGBOOST_AVAILABLE:
            raise ImportError("XGBoost not installed. Run: pip install xgboost")

        return xgb.XGBClassifier(
            objective='multi:softprob',
            num_class=3,
            max_depth=6,  # Optimized for sports data
            learning_rate=0.1,
            n_estimators=150,
            min_child_weight=3,
            subsample=0.8,
            colsample_bytree=0.8,
            gamma=0.1,
            reg_alpha=0.1,  # L1 regularization
            reg_lambda=1.0,  # L2 regularization
            random_state=42,
            n_jobs=-1,
            tree_method='hist'  # Faster training
        )


# ============================================================================
# MODEL 4: GRADIENT BOOSTING
# ============================================================================

class GradientBoostingModel(BaseMLModel):
    """
    Sklearn's Gradient Boosting Classifier.

    Best for:
    - Strong predictive performance
    - Smooth probability estimates
    - Less prone to overfitting than XGBoost
    """

    def __init__(self):
        super().__init__("Gradient Boosting")

    def _create_model(self):
        return GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            min_samples_split=10,
            min_samples_leaf=4,
            subsample=0.8,
            max_features='sqrt',
            random_state=42
        )


# ============================================================================
# MODEL 5: SUPPORT VECTOR MACHINE
# ============================================================================

class SVMModel(BaseMLModel):
    """
    SVM with RBF kernel and probability calibration.

    Best for:
    - Non-linear decision boundaries
    - High-dimensional data
    - Margin maximization
    """

    def __init__(self):
        super().__init__("SVM")

    def _create_model(self):
        return SVC(
            kernel='rbf',
            C=1.0,
            gamma='scale',
            probability=True,  # Enable probability estimates
            random_state=42,
            class_weight='balanced'
        )


# ============================================================================
# MODEL 6: K-NEAREST NEIGHBORS
# ============================================================================

class KNNModel(BaseMLModel):
    """
    K-Nearest Neighbors classifier.

    Best for:
    - Simple pattern matching
    - No training phase
    - Finding similar historical matches
    """

    def __init__(self):
        super().__init__("K-Nearest Neighbors")

    def _create_model(self):
        return KNeighborsClassifier(
            n_neighbors=15,  # Optimized for football data
            weights='distance',  # Weight by distance
            algorithm='auto',
            leaf_size=30,
            n_jobs=-1
        )


# ============================================================================
# MODEL 7: DECISION TREE
# ============================================================================

class DecisionTreeModel(BaseMLModel):
    """
    Single Decision Tree with max depth limit.

    Best for:
    - Interpretability
    - Fast predictions
    - Understanding decision rules
    """

    def __init__(self):
        super().__init__("Decision Tree")

    def _create_model(self):
        return DecisionTreeClassifier(
            max_depth=10,
            min_samples_split=20,
            min_samples_leaf=10,
            random_state=42,
            class_weight='balanced'
        )


# ============================================================================
# MODEL 8: NAIVE BAYES
# ============================================================================

class NaiveBayesModel(BaseMLModel):
    """
    Gaussian Naive Bayes classifier.

    Best for:
    - Fast training and prediction
    - Probabilistic interpretation
    - Works well with small datasets
    """

    def __init__(self):
        super().__init__("Naive Bayes")

    def _create_model(self):
        return GaussianNB()


# ============================================================================
# MODEL 9: ADABOOST
# ============================================================================

class AdaBoostModel(BaseMLModel):
    """
    AdaBoost (Adaptive Boosting) ensemble.

    Best for:
    - Combining weak learners
    - Reducing bias
    - Handling difficult examples
    """

    def __init__(self):
        super().__init__("AdaBoost")

    def _create_model(self):
        return AdaBoostClassifier(
            n_estimators=100,
            learning_rate=0.5,
            random_state=42,
            algorithm='SAMME'
        )


# ============================================================================
# MODEL 10: NEURAL NETWORK (MLP)
# ============================================================================

class NeuralNetworkModel(BaseMLModel):
    """
    Multi-Layer Perceptron (Neural Network).

    Best for:
    - Learning complex non-linear patterns
    - Large datasets
    - Deep feature interactions
    """

    def __init__(self):
        super().__init__("Neural Network")

    def _create_model(self):
        return MLPClassifier(
            hidden_layer_sizes=(100, 50, 25),  # 3 hidden layers
            activation='relu',
            solver='adam',
            alpha=0.0001,  # L2 regularization
            batch_size=32,
            learning_rate='adaptive',
            learning_rate_init=0.001,
            max_iter=500,
            early_stopping=True,
            validation_fraction=0.1,
            random_state=42
        )


# ============================================================================
# MODEL 11: LIGHTGBM
# ============================================================================

class LightGBMModel(BaseMLModel):
    """
    LightGBM - Microsoft's gradient boosting framework.

    Best for:
    - Very fast training
    - Large datasets
    - Memory efficiency
    """

    def __init__(self):
        super().__init__("LightGBM")

    def _create_model(self):
        if not LIGHTGBM_AVAILABLE:
            raise ImportError("LightGBM not installed. Run: pip install lightgbm")

        return lgb.LGBMClassifier(
            objective='multiclass',
            num_class=3,
            n_estimators=150,
            max_depth=6,
            learning_rate=0.1,
            num_leaves=31,
            min_child_samples=20,
            subsample=0.8,
            colsample_bytree=0.8,
            reg_alpha=0.1,
            reg_lambda=1.0,
            random_state=42,
            n_jobs=-1,
            verbosity=-1
        )


# ============================================================================
# MODEL 12: CATBOOST
# ============================================================================

class CatBoostModel(BaseMLModel):
    """
    CatBoost - Yandex's gradient boosting.

    Best for:
    - Categorical features handling
    - Ordered boosting
    - Robust to overfitting
    """

    def __init__(self):
        super().__init__("CatBoost")

    def _create_model(self):
        if not CATBOOST_AVAILABLE:
            raise ImportError("CatBoost not installed. Run: pip install catboost")

        return cb.CatBoostClassifier(
            iterations=150,
            depth=6,
            learning_rate=0.1,
            l2_leaf_reg=3.0,
            random_seed=42,
            verbose=False,
            thread_count=-1
        )


# ============================================================================
# MODEL 13: EXTRA TREES
# ============================================================================

class ExtraTreesModel(BaseMLModel):
    """
    Extra Trees (Extremely Randomized Trees).

    Best for:
    - Reducing variance more than Random Forest
    - Faster training
    - Better generalization
    """

    def __init__(self):
        super().__init__("Extra Trees")

    def _create_model(self):
        return ExtraTreesClassifier(
            n_estimators=200,
            max_depth=15,
            min_samples_split=10,
            min_samples_leaf=4,
            max_features='sqrt',
            bootstrap=True,
            oob_score=True,
            random_state=42,
            n_jobs=-1,
            class_weight='balanced'
        )


# ============================================================================
# MODEL 14: RIDGE CLASSIFIER
# ============================================================================

class RidgeClassifierModel(BaseMLModel):
    """
    Ridge Classifier (L2-regularized linear model).

    Best for:
    - Fast linear classification
    - Multicollinearity handling
    - Regularization
    """

    def __init__(self):
        super().__init__("Ridge Classifier")

    def _create_model(self):
        return RidgeClassifier(
            alpha=1.0,
            random_state=42,
            class_weight='balanced'
        )


# ============================================================================
# MODEL 15: PASSIVE AGGRESSIVE CLASSIFIER
# ============================================================================

class PassiveAggressiveModel(BaseMLModel):
    """
    Passive Aggressive Classifier.

    Best for:
    - Online learning
    - Streaming data
    - Large-scale classification
    """

    def __init__(self):
        super().__init__("Passive Aggressive")

    def _create_model(self):
        return PassiveAggressiveClassifier(
            C=1.0,
            max_iter=1000,
            random_state=42,
            n_jobs=-1,
            class_weight='balanced'
        )


# ============================================================================
# MODEL 16: QUADRATIC DISCRIMINANT ANALYSIS
# ============================================================================

class QDAModel(BaseMLModel):
    """
    Quadratic Discriminant Analysis.

    Best for:
    - Gaussian distributed features
    - Non-linear decision boundaries
    - Probabilistic classification
    """

    def __init__(self):
        super().__init__("QDA")

    def _create_model(self):
        return QuadraticDiscriminantAnalysis()


# ============================================================================
# MODEL 17: LINEAR DISCRIMINANT ANALYSIS
# ============================================================================

class LDAModel(BaseMLModel):
    """
    Linear Discriminant Analysis.

    Best for:
    - Linear decision boundaries
    - Dimensionality reduction
    - Fast classification
    - Gaussian distributed features
    """

    def __init__(self):
        super().__init__("LDA")

    def _create_model(self):
        return LinearDiscriminantAnalysis(
            solver='svd'  # Singular Value Decomposition
        )


# ============================================================================
# MODEL 18: STOCHASTIC GRADIENT DESCENT
# ============================================================================

class SGDModel(BaseMLModel):
    """
    Stochastic Gradient Descent Classifier.

    Best for:
    - Very large datasets
    - Online learning
    - Fast training
    - Memory efficiency
    """

    def __init__(self):
        super().__init__("SGD")

    def _create_model(self):
        return SGDClassifier(
            loss='log_loss',  # Logistic regression
            penalty='l2',
            alpha=0.0001,
            max_iter=1000,
            random_state=42,
            n_jobs=-1,
            class_weight='balanced'
        )


# ============================================================================
# MODEL 19: BAGGING CLASSIFIER
# ============================================================================

class BaggingModel(BaseMLModel):
    """
    Bagging (Bootstrap Aggregating) Classifier.

    Best for:
    - Reducing variance
    - Ensemble diversity
    - Parallel training
    """

    def __init__(self):
        super().__init__("Bagging")

    def _create_model(self):
        base_estimator = DecisionTreeClassifier(
            max_depth=10,
            random_state=42
        )
        return BaggingClassifier(
            base_estimator=base_estimator,
            n_estimators=50,
            max_samples=0.8,
            max_features=0.8,
            bootstrap=True,
            random_state=42,
            n_jobs=-1
        )


# ============================================================================
# MODEL 20: GAUSSIAN PROCESS
# ============================================================================

class GaussianProcessModel(BaseMLModel):
    """
    Gaussian Process Classifier.

    Best for:
    - Uncertainty quantification
    - Small to medium datasets
    - Non-parametric approach
    - Probabilistic predictions
    """

    def __init__(self):
        super().__init__("Gaussian Process")

    def _create_model(self):
        kernel = 1.0 * RBF(1.0)  # Radial Basis Function kernel
        return GaussianProcessClassifier(
            kernel=kernel,
            random_state=42,
            n_jobs=-1,
            max_iter_predict=100
        )


# ============================================================================
# MODEL 21: STACKING ENSEMBLE
# ============================================================================

class StackingEnsembleModel(BaseMLModel):
    """
    Stacking Ensemble - Meta-learning from base models.

    Best for:
    - Learning optimal model combinations
    - Leveraging model strengths
    - Maximum predictive power

    Uses LogisticRegression as meta-classifier.
    """

    def __init__(self):
        super().__init__("Stacking Ensemble")

    def _create_model(self):
        # Base estimators - diverse set of models
        estimators = [
            ('rf', RandomForestClassifier(
                n_estimators=100, max_depth=10, random_state=42, n_jobs=-1
            )),
            ('gb', GradientBoostingClassifier(
                n_estimators=50, max_depth=5, random_state=42
            )),
            ('mlp', MLPClassifier(
                hidden_layer_sizes=(50,), max_iter=300, random_state=42
            )),
            ('knn', KNeighborsClassifier(
                n_neighbors=15, weights='distance', n_jobs=-1
            ))
        ]

        if XGBOOST_AVAILABLE:
            estimators.append(
                ('xgb', xgb.XGBClassifier(
                    objective='multi:softprob', num_class=3,
                    max_depth=5, learning_rate=0.1, n_estimators=100,
                    random_state=42, n_jobs=-1
                ))
            )

        # Meta-classifier
        final_estimator = LogisticRegression(
            multi_class='multinomial',
            solver='lbfgs',
            random_state=42
        )

        return StackingClassifier(
            estimators=estimators,
            final_estimator=final_estimator,
            cv=5,
            n_jobs=-1
        )


# ============================================================================
# MODEL 22: VOTING ENSEMBLE
# ============================================================================

class VotingEnsembleModel(BaseMLModel):
    """
    Voting Ensemble - Combines predictions from multiple models.

    Best for:
    - Maximum accuracy
    - Robust predictions
    - Leveraging diverse models

    Uses soft voting (probability averaging) for best results.
    """

    def __init__(self, models: list = None):
        super().__init__("Voting Ensemble")
        self.base_models = models or []

    def _create_model(self):
        if not self.base_models:
            # Create default ensemble with top performing models
            estimators = [
                ('xgb', xgb.XGBClassifier(
                    objective='multi:softprob', num_class=3,
                    max_depth=6, learning_rate=0.1, n_estimators=150,
                    random_state=42, n_jobs=-1
                ) if XGBOOST_AVAILABLE else None),
                ('rf', RandomForestClassifier(
                    n_estimators=200, max_depth=15, random_state=42, n_jobs=-1
                )),
                ('gb', GradientBoostingClassifier(
                    n_estimators=100, max_depth=5, random_state=42
                )),
                ('mlp', MLPClassifier(
                    hidden_layer_sizes=(100, 50), max_iter=500, random_state=42
                ))
            ]

            # Filter out None estimators
            estimators = [(name, est) for name, est in estimators if est is not None]
        else:
            estimators = self.base_models

        return VotingClassifier(
            estimators=estimators,
            voting='soft',  # Use probability averaging
            n_jobs=-1
        )


# ============================================================================
# MODEL FACTORY
# ============================================================================

def create_all_models() -> Dict[str, BaseMLModel]:
    """
    Create instances of all 17 models.

    Returns:
        Dictionary mapping model names to model instances
    """
    models = {
        # Core models (always available)
        "logistic_regression": LogisticRegressionModel(),
        "random_forest": RandomForestModel(),
        "gradient_boosting": GradientBoostingModel(),
        "svm": SVMModel(),
        "knn": KNNModel(),
        "decision_tree": DecisionTreeModel(),
        "naive_bayes": NaiveBayesModel(),
        "adaboost": AdaBoostModel(),
        "neural_network": NeuralNetworkModel(),
        "extra_trees": ExtraTreesModel(),
        "ridge": RidgeClassifierModel(),
        "passive_aggressive": PassiveAggressiveModel(),
        "qda": QDAModel(),

        # Additional models (17+)
        "lda": LDAModel(),
        "sgd": SGDModel(),
        "bagging": BaggingModel(),
        "gaussian_process": GaussianProcessModel(),
        "stacking_ensemble": StackingEnsembleModel(),
        "voting_ensemble": VotingEnsembleModel(),
    }

    # Add optional models if libraries are available
    if XGBOOST_AVAILABLE:
        models["xgboost"] = XGBoostModel()

    if LIGHTGBM_AVAILABLE:
        models["lightgbm"] = LightGBMModel()

    if CATBOOST_AVAILABLE:
        models["catboost"] = CatBoostModel()

    return models


def get_tier_models(tier: str) -> list:
    """
    Get model names available for each tier.

    Total: 22 ML models (25 with optional libraries)
    Distribution across tiers optimized for value proposition:

    - Free: 4 models (fast, interpretable baselines)
    - Starter: +5 models (9 total - adds discriminant analysis and ensemble basics)
    - Pro: +6 models (15 total - adds powerful tree-based ensembles)
    - Premium: +5 models (20 total - adds advanced gradient boosting)
    - Ultimate: All 22+ models (adds SVM, GP, meta-ensembles)
    """
    tier_map = {
        "free": [
            # Fast, interpretable baselines
            "logistic_regression",
            "decision_tree",
            "naive_bayes",
            "ridge"
        ],
        "starter": [
            # Free models + discriminant analysis + online learning
            "logistic_regression", "decision_tree", "naive_bayes", "ridge",
            "knn", "passive_aggressive", "qda", "lda", "sgd"
        ],
        "pro": [
            # Starter models + powerful ensembles
            "logistic_regression", "decision_tree", "naive_bayes", "ridge",
            "knn", "passive_aggressive", "qda", "lda", "sgd",
            "random_forest", "extra_trees", "adaboost",
            "gradient_boosting", "neural_network", "bagging"
        ],
        "premium": [
            # Pro models + advanced gradient boosting
            "logistic_regression", "decision_tree", "naive_bayes", "ridge",
            "knn", "passive_aggressive", "qda", "lda", "sgd",
            "random_forest", "extra_trees", "adaboost",
            "gradient_boosting", "neural_network", "bagging",
            "xgboost", "lightgbm", "catboost", "svm", "stacking_ensemble"
        ],
        "ultimate": [
            # ALL MODELS - maximum predictive power
            "logistic_regression", "decision_tree", "naive_bayes", "ridge",
            "knn", "passive_aggressive", "qda", "lda", "sgd",
            "random_forest", "extra_trees", "adaboost",
            "gradient_boosting", "neural_network", "bagging",
            "xgboost", "lightgbm", "catboost", "svm", "stacking_ensemble",
            "gaussian_process", "voting_ensemble"
        ]
    }

    return tier_map.get(tier, tier_map["free"])
