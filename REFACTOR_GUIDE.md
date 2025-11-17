# Complete 36-Model Refactor Implementation Guide

## Overview
This guide shows how to implement all 36 football prediction models in a unified architecture.

## Architecture Summary

### Base Class Hierarchy
```
BaseComponent (abstract)
├── SupervisedModel (fit/predict_proba) - for classification/regression
├── ScorelineModel (fit/predict_score_matrix) - for full score distributions
├── TotalsModel (fit/pmf) - for totals distributions
├── SurvivalModel (fit/hazard) - for time-to-event
├── RatingModel (update_from_matches/get_rating) - for team ratings
├── SimulationModel (simulate) - for Monte Carlo
├── PreprocessorModel (fit_transform/transform) - for clustering/PCA
└── SequenceModel (fit_sequences/predict_sequence) - for LSTM/Transformer
```

### Model Mapping (All 36)

#### Statistical Models (1-14)
1. ✅ PoissonGoalModel → ScorelineModel
2. ✅ DixonColesPoissonModel → ScorelineModel
3. ✅ BivariatePoissonModel → ScorelineModel
4. ✅ SkellamOutcomeModel → SupervisedModel
5. ✅ NegBinTotalsModel → TotalsModel
6. ✅ ZeroInflatedPoissonModel → ScorelineModel + TotalsModel
7. 🔨 BayesianHierarchicalPoissonModel → ScorelineModel
8. 🔨 OrderedLogitOutcomeModel → SupervisedModel
9. 🔨 GAMOutcomeModel → SupervisedModel
10. ✅ CoxGoalSurvivalModel → SurvivalModel
11. 🔨 CopulaScoreModel → ScorelineModel
12. 🔨 MarkovEPVModel → SimulationModel / custom
13. 🔨 HawkesEventModel → SurvivalModel
14. ✅ XGShotLogisticModel → SupervisedModel

#### Rating Systems (15-17)
15. ✅ EloRatingSystem → RatingModel
16. 🔨 GlickoRatingSystem → RatingModel
17. 🔨 BradleyTerryModel → RatingModel

#### Simulation (18)
18. ✅ ScoreMonteCarloSimulator → SimulationModel

#### Classical ML (19-27)
19. 🔨 LinearRegressionModel → SupervisedModel
20. ✅ LogisticOutcomeModel → SupervisedModel
21. 🔨 DecisionTreeModel → SupervisedModel
22. 🔨 RandomForestModel → SupervisedModel
23. 🔨 KNNModel → SupervisedModel
24. 🔨 NaiveBayesModel → SupervisedModel
25. 🔨 SVMModel → SupervisedModel
26. 🔨 AdaBoostModel → SupervisedModel
27. 🔨 XGBoostModel → SupervisedModel

#### Unsupervised ML (28-30, 35)
28. ✅ KMeansTeamClusterer → PreprocessorModel
29. 🔨 HierarchicalClusterer → PreprocessorModel
30. 🔨 DBSCANClusterer → PreprocessorModel
35. 🔨 GMMClusterer → PreprocessorModel

#### Dimensionality Reduction (31)
31. ✅ PCAMatchReducer → PreprocessorModel

#### Deep Learning (32-34, 36)
32. 🔨 MLPOutcomeModel → SupervisedModel
33. 🔨 CNNOutcomeModel → SequenceModel
34. ✅ LSTMOutcomeSequenceModel → SequenceModel
36. 🔨 TransformerOutcomeModel → SequenceModel

Legend: ✅ = Implemented in PDF, 🔨 = Need to implement

## Implementation Steps

### Step 1: Core Infrastructure (DONE)
- app/core/base.py - Base classes ✅
- app/core/registry.py - Registry system ✅
- app/core/tasks.py - TaskType and Mode enums ✅

### Step 2: Complete All Model Implementations
See individual files below for each model category.

### Step 3: Feature Builders
- app/features/prematch.py - Pre-match features
- app/features/inplay.py - In-play features
- app/features/shot_level.py - Shot-level features for xG
- app/features/sequences.py - Sequences for LSTM/Transformer

### Step 4: Services
- app/services/training.py - Unified training ✅
- app/services/prediction.py - Unified prediction ✅
- app/services/ratings_update.py - Update ratings periodically

### Step 5: API Endpoints
- app/api/routes_predictions.py - Prediction endpoints
- app/api/routes_analysis.py - Analysis endpoints (clustering, PCA, etc.)

## Usage Examples

### Training All Models
```python
from app.services.training import TrainingService
from app.db.session import SessionLocal

session = SessionLocal()
svc = TrainingService(session, league_id=152)

# Train a specific model
svc.train_component("LogisticOutcomeModel")
svc.train_component("PoissonGoalModel")
svc.train_component("XGBoostModel")

# Or train all registered models
from app.core.registry import list_components
for name in list_components().keys():
    try:
        svc.train_component(name)
    except Exception as e:
        print(f"Failed to train {name}: {e}")
```

### Making Predictions
```python
from app.services.prediction import PredictionService

svc = PredictionService(session, league_id=152)

# Pre-match prediction with multiple models
result = svc.prematch_outcome(
    match_id=123456,
    model_names=["LogisticOutcomeModel", "RandomForestModel", "XGBoostModel"]
)
# Returns: {"LogisticOutcomeModel": {"home_win": 0.45, "draw": 0.28, "away_win": 0.27}, ...}

# In-play prediction
result = svc.inplay_outcome(
    live_event_json=event_data,
    model_names=["LSTMOutcomeSequenceModel"]
)
```

### API Usage
```bash
# Train models
curl -X POST http://localhost:8000/train \
  -H "Content-Type: application/json" \
  -d '{"models": ["LogisticOutcomeModel", "XGBoostModel"], "league_id": 152}'

# Get predictions
curl -X POST http://localhost:8000/predictions/prematch \
  -H "Content-Type: application/json" \
  -d '{
    "match_id": 123456,
    "league_id": 152,
    "models": ["LogisticOutcomeModel", "RandomForestModel", "PoissonGoalModel"]
  }'
```

## Next Steps

1. Implement remaining model stubs (marked with 🔨)
2. Implement feature builders
3. Create comprehensive tests
4. Add model performance tracking
5. Implement model versioning
6. Add caching layer
7. Create frontend dashboard
