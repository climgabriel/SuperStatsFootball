from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import json

from app.core.dependencies import get_db, get_current_active_user
from app.core.security import check_model_access
from app.models.user import User
from app.models.fixture import Fixture
from app.models.prediction import Prediction
from app.schemas.prediction import PredictionRequest, PredictionResponse

router = APIRouter()


@router.post("/calculate", response_model=PredictionResponse)
async def calculate_prediction(
    prediction_request: PredictionRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Calculate prediction for a fixture using specified model.

    Available models depend on user's subscription tier:
    - Free: poisson
    - Starter: poisson, dixon_coles
    - Pro: poisson, dixon_coles, elo
    - Premium: poisson, dixon_coles, elo, logistic
    - Ultimate: all models including random_forest, xgboost
    """
    # Check if user has access to this model
    if not check_model_access(current_user.tier, prediction_request.model_type):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Your {current_user.tier} tier does not have access to {prediction_request.model_type} model"
        )

    # Check if fixture exists
    fixture = db.query(Fixture).filter(Fixture.id == prediction_request.fixture_id).first()
    if not fixture:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Fixture {prediction_request.fixture_id} not found"
        )

    # For now, return mock prediction
    # TODO: Implement actual prediction models
    mock_prediction_data = {
        "home_win_prob": 0.45,
        "draw_prob": 0.25,
        "away_win_prob": 0.30,
        "predicted_home_score": 1.8,
        "predicted_away_score": 1.2,
        "most_likely_score": "2-1",
        "model_details": {
            "model": prediction_request.model_type,
            "note": "This is a mock prediction. Actual models will be implemented."
        }
    }

    # Save prediction
    prediction = Prediction(
        fixture_id=prediction_request.fixture_id,
        user_id=current_user.id,
        model_type=prediction_request.model_type,
        prediction_data=json.dumps(mock_prediction_data),
        confidence_score=0.75,
        is_admin_model=prediction_request.model_type in ["random_forest", "xgboost"]
    )

    db.add(prediction)
    db.commit()
    db.refresh(prediction)

    # Convert to response
    response = PredictionResponse.model_validate(prediction)
    response.prediction_data = mock_prediction_data

    return response


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
