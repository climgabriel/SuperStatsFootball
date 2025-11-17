#!/usr/bin/env python3
"""
ML Models Training Script

Trains all 22 ML models using historical fixture data from the database.

Usage:
    python scripts/train_ml_models.py [--models MODEL1,MODEL2] [--seasons 3]

Examples:
    # Train all models
    python scripts/train_ml_models.py

    # Train specific models
    python scripts/train_ml_models.py --models logistic_regression,random_forest

    # Use data from last 5 seasons
    python scripts/train_ml_models.py --seasons 5
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from typing import List, Dict
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import and_
from app.db.session import SessionLocal
from app.models.fixture import Fixture
from app.ml.features.feature_engineering import FeatureEngineer
from app.ml.machine_learning import create_all_models, get_tier_models
import numpy as np

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_training_data(
    db,
    num_seasons: int = 3,
    min_fixtures: int = 100
) -> Dict:
    """
    Extract training data from historical fixtures.

    Args:
        db: Database session
        num_seasons: Number of recent seasons to use
        min_fixtures: Minimum number of fixtures required

    Returns:
        Dictionary with features (X) and labels (y)
    """
    logger.info(f"📊 Extracting training data from last {num_seasons} seasons...")

    # Get current year and calculate seasons to include
    current_year = datetime.now().year
    seasons = list(range(current_year - num_seasons, current_year))

    logger.info(f"   Seasons: {seasons}")

    # Get completed fixtures
    fixtures = db.query(Fixture).filter(
        and_(
            Fixture.season.in_(seasons),
            Fixture.status.in_(["FT", "AET", "PEN"]),
            Fixture.score != None
        )
    ).all()

    logger.info(f"   Found {len(fixtures)} completed fixtures")

    if len(fixtures) < min_fixtures:
        logger.warning(f"⚠️  Only {len(fixtures)} fixtures found (minimum: {min_fixtures})")
        logger.warning("   Training may not be optimal with limited data")

    # Initialize feature engineer
    feature_engineer = FeatureEngineer(db)

    X = []  # Features
    y = []  # Labels (0=away win, 1=draw, 2=home win)

    logger.info("🔧 Extracting features from fixtures...")

    successful = 0
    failed = 0

    for i, fixture in enumerate(fixtures):
        if i % 100 == 0 and i > 0:
            logger.info(f"   Processed {i}/{len(fixtures)} fixtures...")

        try:
            # Extract features
            features = feature_engineer.extract_features(
                home_team_id=fixture.home_team_id,
                away_team_id=fixture.away_team_id,
                league_id=fixture.league_id,
                season=fixture.season
            )

            feature_array = features["feature_array"]

            # Get actual result
            home_goals = fixture.score.home_fulltime or 0
            away_goals = fixture.score.away_fulltime or 0

            if home_goals > away_goals:
                label = 2  # Home win
            elif home_goals < away_goals:
                label = 0  # Away win
            else:
                label = 1  # Draw

            X.append(feature_array)
            y.append(label)
            successful += 1

        except Exception as e:
            failed += 1
            if failed <= 5:  # Only log first 5 errors
                logger.warning(f"   Failed to extract features for fixture {fixture.id}: {str(e)}")

    logger.info(f"✅ Feature extraction complete:")
    logger.info(f"   Success: {successful} fixtures")
    logger.info(f"   Failed: {failed} fixtures")
    logger.info(f"   Total features per sample: {len(X[0]) if X else 0}")

    if not X:
        raise ValueError("No training data extracted! Check database has completed fixtures with scores.")

    return {
        "X": np.array(X),
        "y": np.array(y),
        "num_samples": len(X),
        "num_features": len(X[0]) if X else 0,
        "label_distribution": {
            "away_win": np.sum(y == 0),
            "draw": np.sum(y == 1),
            "home_win": np.sum(y == 2)
        }
    }


def train_models(
    training_data: Dict,
    models_to_train: List[str] = None,
    output_dir: str = "models/trained"
) -> Dict:
    """
    Train ML models with the extracted data.

    Args:
        training_data: Dictionary with X and y
        models_to_train: List of model names to train (None = all)
        output_dir: Directory to save trained models

    Returns:
        Dictionary with training results
    """
    X = training_data["X"]
    y = training_data["y"]

    logger.info(f"\n🤖 Training ML Models...")
    logger.info(f"   Samples: {len(X)}")
    logger.info(f"   Features: {X.shape[1]}")
    logger.info(f"   Label distribution:")
    for label, count in training_data["label_distribution"].items():
        logger.info(f"      {label}: {count} ({count/len(y)*100:.1f}%)")

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    logger.info(f"   Output directory: {output_dir}")

    # Create all models
    all_models = create_all_models()

    # Filter models if specified
    if models_to_train:
        all_models = {k: v for k, v in all_models.items() if k in models_to_train}
        logger.info(f"   Training {len(all_models)} selected models")
    else:
        logger.info(f"   Training ALL {len(all_models)} models")

    results = {}
    successful = 0
    failed = 0

    for i, (model_name, model) in enumerate(all_models.items(), 1):
        logger.info(f"\n[{i}/{len(all_models)}] Training {model_name}...")

        try:
            # Train model
            training_result = model.train(X, y, calibrate=True, cv_folds=5)

            # Save trained model
            model_path = os.path.join(output_dir, f"{model_name}.pkl")
            model.save(model_path)

            results[model_name] = {
                "success": True,
                "cv_scores": training_result.get("cv_scores", []),
                "mean_accuracy": training_result.get("mean_cv_score", 0),
                "std_accuracy": training_result.get("std_cv_score", 0),
                "model_path": model_path
            }

            logger.info(f"   ✅ {model_name}: {results[model_name]['mean_accuracy']:.4f} ± {results[model_name]['std_accuracy']:.4f}")
            successful += 1

        except Exception as e:
            logger.error(f"   ❌ {model_name} failed: {str(e)}")
            results[model_name] = {
                "success": False,
                "error": str(e)
            }
            failed += 1

    logger.info(f"\n📊 Training Summary:")
    logger.info(f"   ✅ Successful: {successful}/{len(all_models)}")
    logger.info(f"   ❌ Failed: {failed}/{len(all_models)}")

    return results


def display_tier_summary(results: Dict):
    """Display summary of models by tier."""
    logger.info("\n🎯 Tier-Based Model Summary:")

    tiers = ["free", "starter", "pro", "premium", "ultimate"]

    for tier in tiers:
        tier_models = get_tier_models(tier)
        trained = sum(1 for m in tier_models if results.get(m, {}).get("success", False))
        total = len(tier_models)

        logger.info(f"\n   {tier.upper()}:")
        logger.info(f"      Total: {total} models")
        logger.info(f"      Trained: {trained}/{total}")

        if trained < total:
            missing = [m for m in tier_models if not results.get(m, {}).get("success", False)]
            logger.info(f"      Missing: {', '.join(missing)}")


def main():
    """Main training script."""
    parser = argparse.ArgumentParser(description="Train ML models for football prediction")
    parser.add_argument(
        "--models",
        type=str,
        help="Comma-separated list of models to train (default: all)",
        default=None
    )
    parser.add_argument(
        "--seasons",
        type=int,
        help="Number of recent seasons to use for training (default: 3)",
        default=3
    )
    parser.add_argument(
        "--min-fixtures",
        type=int,
        help="Minimum number of fixtures required (default: 100)",
        default=100
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        help="Output directory for trained models (default: models/trained)",
        default="models/trained"
    )

    args = parser.parse_args()

    # Parse models list
    models_to_train = None
    if args.models:
        models_to_train = [m.strip() for m in args.models.split(",")]
        logger.info(f"🎯 Training specific models: {models_to_train}")

    logger.info("="*80)
    logger.info("🚀 ML Models Training Script")
    logger.info("="*80)

    try:
        # Create database session
        db = SessionLocal()

        # Step 1: Extract training data
        training_data = get_training_data(
            db,
            num_seasons=args.seasons,
            min_fixtures=args.min_fixtures
        )

        # Step 2: Train models
        results = train_models(
            training_data,
            models_to_train=models_to_train,
            output_dir=args.output_dir
        )

        # Step 3: Display summary
        display_tier_summary(results)

        logger.info("\n" + "="*80)
        logger.info("🎉 Training Complete!")
        logger.info("="*80)

        # Close database
        db.close()

        return 0

    except Exception as e:
        logger.error(f"\n❌ Training failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
