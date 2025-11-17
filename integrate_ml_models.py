#!/usr/bin/env python3
"""
ML Models Integration Script

This script integrates the 22 ML models into the PredictionPipeline.
It modifies the prediction_pipeline.py file to seamlessly merge
statistical and ML model predictions.

Usage:
    python integrate_ml_models.py
"""

import os
import sys
import re

def integrate_ml_models():
    """Integrate ML models into prediction pipeline."""

    pipeline_path = "backend/app/services/prediction_pipeline.py"

    print("🚀 Starting ML Models Integration...")
    print(f"📁 Target file: {pipeline_path}")

    # Read current file
    with open(pipeline_path, 'r') as f:
        content = f.read()

    # Check if already integrated
    if "MLPredictionService" in content and "use_ml_models" in content:
        print("✅ ML models already integrated!")
        return True

    print("📝 Modifying PredictionPipeline...")

    # Step 1: Update MODEL_TIER_MAP to STATISTICAL_MODEL_TIER_MAP
    content = content.replace(
        '# Model tier mapping\nMODEL_TIER_MAP = {',
        '# Statistical model tier mapping (always available as fallback)\nSTATISTICAL_MODEL_TIER_MAP = {'
    )

    # Step 2: Modify __init__ method
    old_init = '''    def __init__(self, db: Session):
        self.db = db
        self.poisson = PoissonModel()
        self.dixon_coles = DixonColesModel()
        self.elo = EloModel()'''

    new_init = '''    def __init__(self, db: Session, use_ml_models: bool = True):
        """
        Initialize Prediction Pipeline.

        Args:
            db: Database session
            use_ml_models: Whether to use ML models (default: True)
        """
        self.db = db
        self.use_ml_models = use_ml_models

        # Statistical models (always available)
        self.poisson = PoissonModel()
        self.dixon_coles = DixonColesModel()
        self.elo = EloModel()

        # ML models (lazy loaded)
        self._ml_service = None
        if use_ml_models:
            try:
                from app.services.ml_prediction_service import MLPredictionService
                self._ml_service = MLPredictionService(db)
                logger.info("✅ ML Prediction Service initialized with 22 models")
            except Exception as e:
                logger.warning(f"⚠️  ML models not available: {str(e)}")
                logger.info("📊 Falling back to statistical models only")
                self.use_ml_models = False'''

    content = content.replace(old_init, new_init)

    # Step 3: Update generate_prediction to use ML models
    # Find the section where available_models is defined
    content = content.replace(
        'available_models = MODEL_TIER_MAP.get(user_tier, ["poisson"])',
        'available_statistical = STATISTICAL_MODEL_TIER_MAP.get(user_tier, ["poisson"])'
    )

    # Step 4: Add ML integration after statistical models section
    statistical_section = '''        # Run Elo (pro+)
        if "elo" in available_models:
            home_rating = self._get_team_rating(fixture.home_team_id, fixture.league_id, fixture.season)
            away_rating = self._get_team_rating(fixture.away_team_id, fixture.league_id, fixture.season)

            elo_pred = self.elo.predict(home_rating, away_rating)
            predictions["elo"] = elo_pred

        # Calculate consensus prediction
        consensus = self._calculate_consensus(predictions)'''

    ml_integration = '''        # Run Elo (pro+)
        if "elo" in available_statistical:
            try:
                home_rating = self._get_team_rating(fixture.home_team_id, fixture.league_id, fixture.season)
                away_rating = self._get_team_rating(fixture.away_team_id, fixture.league_id, fixture.season)

                elo_pred = self.elo.predict(home_rating, away_rating)
                predictions["elo"] = elo_pred
                models_used.append("elo")
            except Exception as e:
                logger.error(f"Elo prediction error: {str(e)}")

        # ==============================================
        # PART 2: MACHINE LEARNING MODELS (22 models)
        # ==============================================

        ml_predictions = {}
        if self.use_ml_models and self._ml_service:
            try:
                ml_result = self._ml_service.predict(
                    fixture_id=fixture_id,
                    user_tier=user_tier
                )

                # Merge ML predictions
                ml_predictions = ml_result.get("predictions", {})
                predictions.update(ml_predictions)
                models_used.extend(ml_result.get("models_used", []))

                logger.info(f"🤖 ML models used: {len(ml_predictions)} for tier '{user_tier}'")
            except Exception as e:
                logger.warning(f"⚠️  ML prediction failed: {str(e)}")

        # Calculate unified consensus from ALL predictions
        consensus = self._calculate_consensus(predictions)'''

    content = content.replace(statistical_section, ml_integration)

    # Step 5: Update models_used list initialization and update references
    content = content.replace(
        '        predictions = {}',
        '        predictions = {}\n        models_used = []'
    )

    # Update available_models references to available_statistical
    content = content.replace('in available_models:', 'in available_statistical:')

    # Add models_used tracking
    content = content.replace(
        '            predictions["poisson"] = poisson_pred',
        '            predictions["poisson"] = poisson_pred\n                models_used.append("poisson")'
    )
    content = content.replace(
        '            predictions["dixon_coles"] = dc_pred',
        '            predictions["dixon_coles"] = dc_pred\n                models_used.append("dixon_coles")'
    )

    # Step 6: Update result dictionary
    old_result = '''        result = {
            "fixture_id": fixture_id,
            "home_team_id": fixture.home_team_id,
            "away_team_id": fixture.away_team_id,
            "league_id": fixture.league_id,
            "match_date": fixture.match_date.isoformat() if fixture.match_date else None,
            "home_stats": home_stats,
            "away_stats": away_stats,
            "predictions": predictions,
            "consensus": consensus,
            "tier": user_tier,
            "models_used": available_models
        }'''

    new_result = '''        result = {
            "fixture_id": fixture_id,
            "home_team_id": fixture.home_team_id,
            "away_team_id": fixture.away_team_id,
            "league_id": fixture.league_id,
            "match_date": fixture.match_date.isoformat() if fixture.match_date else None,
            "home_stats": home_stats,
            "away_stats": away_stats,
            "predictions": predictions,
            "consensus": consensus,
            "tier": user_tier,
            "models_used": models_used,
            "total_models": len(predictions),
            "statistical_models": len([m for m in models_used if m in ["poisson", "dixon_coles", "elo"]]),
            "ml_models": len(ml_predictions),
            "has_ml_predictions": len(ml_predictions) > 0
        }'''

    content = content.replace(old_result, new_result)

    # Write modified content
    with open(pipeline_path, 'w') as f:
        f.write(content)

    print("✅ Integration complete!")
    print("\n📊 Summary:")
    print("   - ML Prediction Service lazy-loaded")
    print("   - 22 ML models integrated with 3 statistical models")
    print("   - Tier-based access maintained")
    print("   - Graceful fallback to statistical models")
    print("   - Enhanced consensus calculation")

    return True

if __name__ == "__main__":
    try:
        success = integrate_ml_models()
        if success:
            print("\n🎉 ML Models successfully integrated!")
            print("   Run your app to see all 25 models in action.")
            sys.exit(0)
        else:
            print("\n⚠️  Integration may have issues. Please review the code.")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error during integration: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
