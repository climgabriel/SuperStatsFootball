"""
Combined Predictions & Odds Endpoint

Provides unified response with:
- Bookmaker odds (from API-Football/Superbet)
- ML predictions (Poisson, Dixon-Coles, Elo based on tier)
- Calculated probabilities
- True odds (1 / probability)
- Draw No Bet calculations
- Double Chance calculations
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import logging

from app.core.dependencies import get_db, get_current_active_user
from app.models.user import User
from app.models.fixture import Fixture
from app.models.odds import FixtureOdds
from app.models.league import League
from app.models.team import Team
from app.services.prediction_pipeline import PredictionPipeline
from app.core.leagues_config import get_leagues_for_tier

router = APIRouter()
logger = logging.getLogger(__name__)


def calculate_true_odds(probability: float) -> float:
    """
    Calculate true odds from probability.

    Args:
        probability: Probability as decimal (0.0 to 1.0)

    Returns:
        True odds as decimal (e.g., 2.50)
    """
    if probability <= 0:
        return 0.0
    return round(1.0 / probability, 2)


def calculate_draw_no_bet(home_prob: float, away_prob: float) -> Dict[str, float]:
    """
    Calculate Draw No Bet odds from win probabilities.
    Redistributes draw probability across home/away.

    Returns:
        Dictionary with '1_dnb' and '2_dnb' odds
    """
    if home_prob + away_prob == 0:
        return {"1_dnb": 0.0, "2_dnb": 0.0}

    # Normalize without draw
    total_prob = home_prob + away_prob
    home_dnb_prob = home_prob / total_prob
    away_dnb_prob = away_prob / total_prob

    return {
        "1_dnb": calculate_true_odds(home_dnb_prob),
        "2_dnb": calculate_true_odds(away_dnb_prob)
    }


def calculate_double_chance(home_prob: float, draw_prob: float, away_prob: float) -> Dict[str, float]:
    """
    Calculate Double Chance odds.

    Returns:
        Dictionary with '1X', 'X2', '12' odds
    """
    return {
        "1X": calculate_true_odds(home_prob + draw_prob),  # Home or Draw
        "X2": calculate_true_odds(draw_prob + away_prob),  # Draw or Away
        "12": calculate_true_odds(home_prob + away_prob)   # Home or Away
    }


@router.get("/fixtures/predictions-with-odds")
async def get_fixtures_with_predictions_and_odds(
    days_ahead: int = Query(7, ge=1, le=30, description="Number of days to look ahead"),
    league_id: Optional[int] = Query(None, description="Filter by league ID"),
    season: Optional[int] = Query(None, description="Filter by season"),
    limit: int = Query(100, ge=1, le=200, description="Max results"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    **UNIFIED ENDPOINT**: Get upcoming fixtures with:
    - Bookmaker odds (Superbet)
    - ML predictions (Poisson, Dixon-Coles, Elo based on user tier)
    - Probability percentages (from ML models)
    - True odds (calculated from probabilities)
    - Draw No Bet odds
    - Double Chance odds

    This endpoint combines data from multiple sources to provide
    everything needed for the frontend 1X2 statistics table.
    """
    try:
        # Calculate date range
        now = datetime.utcnow()
        end_date = now + timedelta(days=days_ahead)

        # Get accessible leagues based on user tier
        accessible_league_ids = get_leagues_for_tier(current_user.tier)

        # Build query
        query = db.query(Fixture).filter(
            Fixture.match_date >= now,
            Fixture.match_date <= end_date,
            Fixture.status.in_(["NS", "TBD"]),  # Not started
            Fixture.league_id.in_(accessible_league_ids)  # Tier-based filtering
        )

        if league_id:
            if league_id not in accessible_league_ids:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"League {league_id} not accessible with {current_user.tier} tier"
                )
            query = query.filter(Fixture.league_id == league_id)

        if season:
            query = query.filter(Fixture.season == season)

        # Get total count
        total = query.count()

        # Get fixtures with relationships loaded
        fixtures = query.options(
            joinedload(Fixture.odds),
            joinedload(Fixture.league),
            joinedload(Fixture.home_team),
            joinedload(Fixture.away_team)
        ).order_by(Fixture.match_date).limit(limit).offset(offset).all()

        # Initialize prediction pipeline
        prediction_pipeline = PredictionPipeline(db)

        # Transform fixtures to response format
        result_fixtures = []

        for fixture in fixtures:
            try:
                # Get Superbet odds
                odds_obj = next(
                    (o for o in fixture.odds if o.bookmaker_name == "Superbet" and not o.is_live),
                    None
                )

                # Generate ML predictions
                try:
                    prediction_data = prediction_pipeline.generate_prediction(
                        fixture_id=fixture.id,
                        user_tier=current_user.tier
                    )

                    # Extract consensus probabilities (these are percentages, e.g., 45.5)
                    consensus = prediction_data.get("consensus", {})
                    home_prob_pct = consensus.get("home_win", 33.33)
                    draw_prob_pct = consensus.get("draw", 33.33)
                    away_prob_pct = consensus.get("away_win", 33.33)

                    # Convert to decimals for calculations
                    home_prob = home_prob_pct / 100.0
                    draw_prob = draw_prob_pct / 100.0
                    away_prob = away_prob_pct / 100.0

                    # Calculate true odds from ML probabilities
                    ht_true_odds = {
                        "1": calculate_true_odds(home_prob),
                        "X": calculate_true_odds(draw_prob),
                        "2": calculate_true_odds(away_prob)
                    }

                    ft_true_odds = ht_true_odds  # Same for simplicity (can be enhanced)

                    # Calculate derived bets
                    ht_dnb = calculate_draw_no_bet(home_prob, away_prob)
                    ft_dnb = ht_dnb

                    ht_dc = calculate_double_chance(home_prob, draw_prob, away_prob)
                    ft_dc = ht_dc

                except Exception as pred_error:
                    logger.warning(f"Prediction failed for fixture {fixture.id}: {str(pred_error)}")
                    # Fallback to default values
                    home_prob_pct = draw_prob_pct = away_prob_pct = 33.33
                    ht_true_odds = ft_true_odds = {"1": 3.00, "X": 3.00, "2": 3.00}
                    ht_dnb = ft_dnb = {"1_dnb": 2.00, "2_dnb": 2.00}
                    ht_dc = ft_dc = {"1X": 1.50, "X2": 1.50, "12": 1.50}

                # Build response object
                match_data = {
                    "fixture_id": fixture.id,
                    "league": fixture.league.name if fixture.league else f"League {fixture.league_id}",
                    "date": fixture.match_date.strftime("%d-%m-%Y") if fixture.match_date else "",
                    "team1": fixture.home_team.name if fixture.home_team else f"Team {fixture.home_team_id}",
                    "team2": fixture.away_team.name if fixture.away_team else f"Team {fixture.away_team_id}",

                    # Half Time data
                    "half_time": {
                        "bookmaker_odds": {
                            "1": odds_obj.ht_home_win_odds if odds_obj and odds_obj.ht_home_win_odds else "-",
                            "X": odds_obj.ht_draw_odds if odds_obj and odds_obj.ht_draw_odds else "-",
                            "2": odds_obj.ht_away_win_odds if odds_obj and odds_obj.ht_away_win_odds else "-"
                        },
                        "probability": {
                            "1": f"{home_prob_pct:.1f}%",
                            "X": f"{draw_prob_pct:.1f}%",
                            "2": f"{away_prob_pct:.1f}%"
                        },
                        "true_odds": {
                            "1": f"{ht_true_odds['1']:.2f}",
                            "X": f"{ht_true_odds['X']:.2f}",
                            "2": f"{ht_true_odds['2']:.2f}"
                        }
                    },

                    # Full Time data
                    "full_time": {
                        "bookmaker_odds": {
                            "1": odds_obj.home_win_odds if odds_obj and odds_obj.home_win_odds else "-",
                            "X": odds_obj.draw_odds if odds_obj and odds_obj.draw_odds else "-",
                            "2": odds_obj.away_win_odds if odds_obj and odds_obj.away_win_odds else "-"
                        },
                        "probability": {
                            "1": f"{home_prob_pct:.1f}%",
                            "X": f"{draw_prob_pct:.1f}%",
                            "2": f"{away_prob_pct:.1f}%"
                        },
                        "true_odds": {
                            "1": f"{ft_true_odds['1']:.2f}",
                            "X": f"{ft_true_odds['X']:.2f}",
                            "2": f"{ft_true_odds['2']:.2f}"
                        }
                    },

                    # Draw No Bet
                    "draw_no_bet": {
                        "half_time": {
                            "1_dnb": f"{ht_dnb['1_dnb']:.2f}",
                            "2_dnb": f"{ht_dnb['2_dnb']:.2f}"
                        },
                        "full_time": {
                            "1_dnb": f"{ft_dnb['1_dnb']:.2f}",
                            "2_dnb": f"{ft_dnb['2_dnb']:.2f}"
                        }
                    },

                    # Double Chance
                    "double_chance": {
                        "half_time": {
                            "1X": f"{ht_dc['1X']:.2f}",
                            "X2": f"{ht_dc['X2']:.2f}",
                            "12": f"{ht_dc['12']:.2f}"
                        },
                        "full_time": {
                            "1X": f"{ft_dc['1X']:.2f}",
                            "X2": f"{ft_dc['X2']:.2f}",
                            "12": f"{ft_dc['12']:.2f}"
                        }
                    },

                    # Metadata
                    "status": fixture.status,
                    "models_used": prediction_data.get("models_used", ["poisson"]) if 'prediction_data' in locals() else ["poisson"],
                    "tier": current_user.tier
                }

                result_fixtures.append(match_data)

            except Exception as fixture_error:
                logger.error(f"Error processing fixture {fixture.id}: {str(fixture_error)}")
                continue

        return {
            "total": total,
            "count": len(result_fixtures),
            "days_ahead": days_ahead,
            "user_tier": current_user.tier,
            "fixtures": result_fixtures
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in predictions endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating predictions: {str(e)}"
        )
