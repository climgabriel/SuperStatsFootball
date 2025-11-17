from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import json

from app.core.dependencies import get_db, get_current_active_user
from app.core.security import check_model_access
from app.core.config import settings
from app.models.user import User
from app.models.fixture import Fixture
from app.models.prediction import Prediction
from app.schemas.prediction import PredictionRequest, PredictionResponse
from app.services.prediction_pipeline import PredictionPipeline
from app.utils.validators import validate_league_count

router = APIRouter()


@router.post("/calculate")
async def calculate_prediction(
    prediction_request: PredictionRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Calculate prediction for a fixture using all tier-appropriate models.

    Available models depend on user's subscription tier:
    - Free: poisson
    - Starter: poisson, dixon_coles
    - Pro: poisson, dixon_coles, elo
    - Premium: poisson, dixon_coles, elo, logistic
    - Ultimate: all models including random_forest, xgboost
    """
    # Check if fixture exists
    fixture = db.query(Fixture).filter(Fixture.id == prediction_request.fixture_id).first()
    if not fixture:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Fixture {prediction_request.fixture_id} not found"
        )

    # Generate prediction using pipeline
    try:
        pipeline = PredictionPipeline(db)
        prediction_data = pipeline.generate_prediction(
            fixture_id=prediction_request.fixture_id,
            user_tier=current_user.tier
        )

        # Store prediction in database
        stored_prediction = pipeline.store_prediction(prediction_data, current_user.id)

        return {
            "id": stored_prediction.id,
            "fixture_id": stored_prediction.fixture_id,
            "user_id": stored_prediction.user_id,
            "prediction_data": prediction_data,
            "created_at": stored_prediction.created_at,
            "message": f"Prediction generated using {len(prediction_data['models_used'])} models"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating prediction: {str(e)}"
        )


@router.get("/{fixture_id}", response_model=List[PredictionResponse])
async def get_predictions(
    fixture_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all predictions for a fixture by the current user.
    """
    predictions = db.query(Prediction).filter(
        Prediction.fixture_id == fixture_id,
        Prediction.user_id == current_user.id
    ).all()

    # Convert predictions to response format
    responses = []
    for pred in predictions:
        resp = PredictionResponse.model_validate(pred)
        resp.prediction_data = json.loads(pred.prediction_data)
        responses.append(resp)

    return responses


@router.get("/user/history", response_model=List[PredictionResponse])
async def get_user_predictions(
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's prediction history.
    """
    predictions = db.query(Prediction).filter(
        Prediction.user_id == current_user.id
    ).order_by(
        Prediction.created_at.desc()
    ).offset(offset).limit(limit).all()

    # Convert predictions to response format
    responses = []
    for pred in predictions:
        resp = PredictionResponse.model_validate(pred)
        resp.prediction_data = json.loads(pred.prediction_data)
        responses.append(resp)

    return responses


@router.get("/upcoming")
async def get_upcoming_predictions(
    league_id: Optional[int] = Query(None, description="Filter by single league ID (deprecated, use league_ids)"),
    league_ids: Optional[List[int]] = Query(None, description="Filter by multiple league IDs (max 5 for regular users, 10 for admin)"),
    days_ahead: int = Query(7, ge=1, le=30, description="Number of days to look ahead"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Generate predictions for upcoming fixtures.

    Query Parameters:
    - league_id: Optional filter by single league (deprecated)
    - league_ids: Optional filter by multiple leagues (max 5 for regular users, 10 for admin)
    - days_ahead: Number of days to look ahead (default: 7, max: 30)

    Returns predictions using all models available to user's tier.
    """
    try:
        # Handle league filtering (support both single and multiple league IDs)
        requested_league_ids = []
        if league_ids:
            requested_league_ids = league_ids
        elif league_id:
            # Backward compatibility: convert single league_id to list
            requested_league_ids = [league_id]

        # Validate league count to prevent app crashes
        if requested_league_ids:
            validate_league_count(
                league_ids=requested_league_ids,
                user_tier=current_user.tier,
                max_regular=settings.MAX_LEAGUES_PER_SEARCH_REGULAR,
                max_admin=settings.MAX_LEAGUES_PER_SEARCH_ADMIN
            )

        # Use first league ID for backward compatibility with pipeline
        # TODO: Update pipeline to support multiple league IDs
        single_league_id = requested_league_ids[0] if requested_league_ids else None

        pipeline = PredictionPipeline(db)
        predictions = pipeline.generate_predictions_for_upcoming(
            league_id=single_league_id,
            days_ahead=days_ahead,
            user_tier=current_user.tier
        )

        return {
            "count": len(predictions),
            "days_ahead": days_ahead,
            "league_id": single_league_id,
            "league_ids": requested_league_ids if requested_league_ids else None,
            "user_tier": current_user.tier,
            "predictions": predictions
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating upcoming predictions: {str(e)}"
        )
