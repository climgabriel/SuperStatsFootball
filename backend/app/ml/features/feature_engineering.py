"""
Feature Engineering Pipeline for ML Models

Extracts comprehensive features from database for machine learning predictions.
ALL features are calculated from historical match data ONLY (no bookmaker odds).

Features extracted:
- Team form and recent performance
- Goals scored/conceded statistics
- Shots and possession metrics
- Expected goals (xG)
- Head-to-head records
- Home/away performance splits
- Goal difference and win ratios
- Moving averages and trends
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
import logging

from app.models.fixture import Fixture, FixtureStat, FixtureScore
from app.models.prediction import TeamRating

logger = logging.getLogger(__name__)


class FeatureEngineer:
    """Extract features from database for ML predictions."""

    def __init__(self, db: Session):
        self.db = db

    def extract_features(
        self,
        home_team_id: int,
        away_team_id: int,
        league_id: int,
        season: int,
        lookback_matches: int = 10
    ) -> Dict:
        """
        Extract comprehensive features for a match prediction.

        Args:
            home_team_id: Home team ID
            away_team_id: Away team ID
            league_id: League ID
            season: Season year
            lookback_matches: Number of recent matches to analyze

        Returns:
            Dictionary with feature vectors for ML models
        """
        # Get recent matches for both teams
        home_recent = self._get_recent_matches(home_team_id, league_id, season, lookback_matches)
        away_recent = self._get_recent_matches(away_team_id, league_id, season, lookback_matches)

        # Extract team-specific features
        home_features = self._extract_team_features(home_team_id, home_recent, is_home=True)
        away_features = self._extract_team_features(away_team_id, away_recent, is_home=False)

        # Head-to-head features
        h2h_features = self._extract_h2h_features(home_team_id, away_team_id, league_id, season)

        # League context features
        league_features = self._extract_league_features(league_id, season)

        # Elo ratings
        home_elo = self._get_elo_rating(home_team_id, league_id, season)
        away_elo = self._get_elo_rating(away_team_id, league_id, season)

        # Combine all features
        feature_dict = {
            # Home team features (25 features)
            "home_goals_scored_avg": home_features["goals_scored_avg"],
            "home_goals_conceded_avg": home_features["goals_conceded_avg"],
            "home_goals_diff_avg": home_features["goals_diff_avg"],
            "home_points_last_5": home_features["points_last_5"],
            "home_win_rate": home_features["win_rate"],
            "home_draw_rate": home_features["draw_rate"],
            "home_loss_rate": home_features["loss_rate"],
            "home_shots_avg": home_features["shots_avg"],
            "home_shots_on_target_avg": home_features["shots_on_target_avg"],
            "home_possession_avg": home_features["possession_avg"],
            "home_xg_avg": home_features["xg_avg"],
            "home_xg_conceded_avg": home_features["xg_conceded_avg"],
            "home_corners_avg": home_features["corners_avg"],
            "home_fouls_avg": home_features["fouls_avg"],
            "home_yellow_cards_avg": home_features["yellow_cards_avg"],
            "home_clean_sheets_rate": home_features["clean_sheets_rate"],
            "home_btts_rate": home_features["btts_rate"],  # Both teams to score
            "home_over_2_5_rate": home_features["over_2_5_rate"],
            "home_first_half_goals_avg": home_features["first_half_goals_avg"],
            "home_second_half_goals_avg": home_features["second_half_goals_avg"],
            "home_form_trend": home_features["form_trend"],
            "home_attack_strength": home_features["attack_strength"],
            "home_defense_strength": home_features["defense_strength"],
            "home_elo": home_elo,
            "home_matches_played": home_features["matches_played"],

            # Away team features (25 features)
            "away_goals_scored_avg": away_features["goals_scored_avg"],
            "away_goals_conceded_avg": away_features["goals_conceded_avg"],
            "away_goals_diff_avg": away_features["goals_diff_avg"],
            "away_points_last_5": away_features["points_last_5"],
            "away_win_rate": away_features["win_rate"],
            "away_draw_rate": away_features["draw_rate"],
            "away_loss_rate": away_features["loss_rate"],
            "away_shots_avg": away_features["shots_avg"],
            "away_shots_on_target_avg": away_features["shots_on_target_avg"],
            "away_possession_avg": away_features["possession_avg"],
            "away_xg_avg": away_features["xg_avg"],
            "away_xg_conceded_avg": away_features["xg_conceded_avg"],
            "away_corners_avg": away_features["corners_avg"],
            "away_fouls_avg": away_features["fouls_avg"],
            "away_yellow_cards_avg": away_features["yellow_cards_avg"],
            "away_clean_sheets_rate": away_features["clean_sheets_rate"],
            "away_btts_rate": away_features["btts_rate"],
            "away_over_2_5_rate": away_features["over_2_5_rate"],
            "away_first_half_goals_avg": away_features["first_half_goals_avg"],
            "away_second_half_goals_avg": away_features["second_half_goals_avg"],
            "away_form_trend": away_features["form_trend"],
            "away_attack_strength": away_features["attack_strength"],
            "away_defense_strength": away_features["defense_strength"],
            "away_elo": away_elo,
            "away_matches_played": away_features["matches_played"],

            # Head-to-head features (10 features)
            "h2h_home_wins": h2h_features["home_wins"],
            "h2h_draws": h2h_features["draws"],
            "h2h_away_wins": h2h_features["away_wins"],
            "h2h_home_goals_avg": h2h_features["home_goals_avg"],
            "h2h_away_goals_avg": h2h_features["away_goals_avg"],
            "h2h_total_matches": h2h_features["total_matches"],
            "h2h_over_2_5_rate": h2h_features["over_2_5_rate"],
            "h2h_btts_rate": h2h_features["btts_rate"],
            "h2h_home_win_rate": h2h_features["home_win_rate"],
            "h2h_goals_per_match": h2h_features["goals_per_match"],

            # League context (4 features)
            "league_avg_goals": league_features["avg_goals"],
            "league_avg_home_goals": league_features["avg_home_goals"],
            "league_avg_away_goals": league_features["avg_away_goals"],
            "league_home_win_rate": league_features["home_win_rate"],

            # Relative features (6 features)
            "elo_diff": home_elo - away_elo,
            "attack_diff": home_features["attack_strength"] - away_features["attack_strength"],
            "defense_diff": home_features["defense_strength"] - away_features["defense_strength"],
            "form_diff": home_features["points_last_5"] - away_features["points_last_5"],
            "xg_diff": home_features["xg_avg"] - away_features["xg_avg"],
            "possession_diff": home_features["possession_avg"] - away_features["possession_avg"],
        }

        # Convert to numpy array for ML models (70 features total)
        feature_array = np.array([feature_dict[key] for key in sorted(feature_dict.keys())])

        return {
            "feature_dict": feature_dict,
            "feature_array": feature_array,
            "feature_names": sorted(feature_dict.keys()),
            "total_features": len(feature_dict)
        }

    def _get_recent_matches(
        self,
        team_id: int,
        league_id: int,
        season: int,
        limit: int
    ) -> List[Fixture]:
        """Get recent matches for a team."""
        matches = self.db.query(Fixture).filter(
            and_(
                or_(
                    Fixture.home_team_id == team_id,
                    Fixture.away_team_id == team_id
                ),
                Fixture.league_id == league_id,
                Fixture.season == season,
                Fixture.status.in_(["FT", "AET", "PEN"])
            )
        ).order_by(Fixture.match_date.desc()).limit(limit).all()

        return matches

    def _extract_team_features(
        self,
        team_id: int,
        recent_matches: List[Fixture],
        is_home: bool
    ) -> Dict:
        """Extract features for a single team."""
        if not recent_matches:
            return self._default_team_features()

        goals_scored = []
        goals_conceded = []
        shots = []
        shots_on_target = []
        possession = []
        xg = []
        xg_conceded = []
        corners = []
        fouls = []
        yellow_cards = []
        points = []
        clean_sheets = 0
        btts = 0  # Both teams to score
        over_2_5 = 0
        first_half_goals = []
        second_half_goals = []

        for match in recent_matches:
            is_team_home = match.home_team_id == team_id

            if not match.score:
                continue

            # Goals
            team_goals = match.score.home_fulltime if is_team_home else match.score.away_fulltime
            opp_goals = match.score.away_fulltime if is_team_home else match.score.home_fulltime

            if team_goals is not None and opp_goals is not None:
                goals_scored.append(team_goals)
                goals_conceded.append(opp_goals)

                # Points
                if team_goals > opp_goals:
                    points.append(3)
                elif team_goals == opp_goals:
                    points.append(1)
                else:
                    points.append(0)

                # Clean sheets
                if opp_goals == 0:
                    clean_sheets += 1

                # Both teams to score
                if team_goals > 0 and opp_goals > 0:
                    btts += 1

                # Over 2.5 goals
                if (team_goals + opp_goals) > 2.5:
                    over_2_5 += 1

                # Half time goals
                ht_team = match.score.home_halftime if is_team_home else match.score.away_halftime
                ht_opp = match.score.away_halftime if is_team_home else match.score.home_halftime

                if ht_team is not None and ht_opp is not None:
                    first_half_goals.append(ht_team)
                    second_half_goals.append(team_goals - ht_team if team_goals >= ht_team else 0)

            # Get statistics if available
            stats = self._get_team_stats_for_match(match.id, team_id)
            if stats:
                if stats.total_shots is not None:
                    shots.append(stats.total_shots)
                if stats.shots_on_goal is not None:
                    shots_on_target.append(stats.shots_on_goal)
                if stats.ball_possession is not None:
                    possession.append(stats.ball_possession)
                if stats.expected_goals is not None:
                    xg.append(stats.expected_goals)
                if stats.corners is not None:
                    corners.append(stats.corners)
                if stats.fouls is not None:
                    fouls.append(stats.fouls)
                if stats.yellow_cards is not None:
                    yellow_cards.append(stats.yellow_cards)

            # Get opponent xG
            opp_stats = self._get_team_stats_for_match(
                match.id,
                match.away_team_id if is_team_home else match.home_team_id
            )
            if opp_stats and opp_stats.expected_goals is not None:
                xg_conceded.append(opp_stats.expected_goals)

        # Calculate averages and rates
        matches_played = len(recent_matches)
        matches_with_result = len(goals_scored)

        wins = sum(1 for p in points if p == 3)
        draws = sum(1 for p in points if p == 1)
        losses = sum(1 for p in points if p == 0)

        # Form trend (weighted points - recent matches more important)
        form_trend = 0.0
        if len(points) >= 5:
            weights = [1.5, 1.3, 1.1, 0.9, 0.7]  # Recent matches weighted higher
            weighted_points = sum(p * w for p, w in zip(points[:5], weights))
            form_trend = weighted_points / sum(weights[:len(points[:5])])

        return {
            "goals_scored_avg": np.mean(goals_scored) if goals_scored else 0.0,
            "goals_conceded_avg": np.mean(goals_conceded) if goals_conceded else 0.0,
            "goals_diff_avg": np.mean([g - c for g, c in zip(goals_scored, goals_conceded)]) if goals_scored else 0.0,
            "points_last_5": sum(points[:5]) if len(points) >= 5 else sum(points),
            "win_rate": wins / matches_with_result if matches_with_result > 0 else 0.0,
            "draw_rate": draws / matches_with_result if matches_with_result > 0 else 0.0,
            "loss_rate": losses / matches_with_result if matches_with_result > 0 else 0.0,
            "shots_avg": np.mean(shots) if shots else 0.0,
            "shots_on_target_avg": np.mean(shots_on_target) if shots_on_target else 0.0,
            "possession_avg": np.mean(possession) if possession else 50.0,
            "xg_avg": np.mean(xg) if xg else 1.0,
            "xg_conceded_avg": np.mean(xg_conceded) if xg_conceded else 1.0,
            "corners_avg": np.mean(corners) if corners else 0.0,
            "fouls_avg": np.mean(fouls) if fouls else 0.0,
            "yellow_cards_avg": np.mean(yellow_cards) if yellow_cards else 0.0,
            "clean_sheets_rate": clean_sheets / matches_with_result if matches_with_result > 0 else 0.0,
            "btts_rate": btts / matches_with_result if matches_with_result > 0 else 0.0,
            "over_2_5_rate": over_2_5 / matches_with_result if matches_with_result > 0 else 0.0,
            "first_half_goals_avg": np.mean(first_half_goals) if first_half_goals else 0.0,
            "second_half_goals_avg": np.mean(second_half_goals) if second_half_goals else 0.0,
            "form_trend": form_trend,
            "attack_strength": (np.mean(goals_scored) / 1.5) if goals_scored else 1.0,  # Normalized to league avg
            "defense_strength": (np.mean(goals_conceded) / 1.5) if goals_conceded else 1.0,
            "matches_played": matches_played
        }

    def _get_team_stats_for_match(self, fixture_id: int, team_id: int) -> Optional[FixtureStat]:
        """Get statistics for a team in a specific match."""
        return self.db.query(FixtureStat).filter(
            and_(
                FixtureStat.fixture_id == fixture_id,
                FixtureStat.team_id == team_id
            )
        ).first()

    def _extract_h2h_features(
        self,
        home_team_id: int,
        away_team_id: int,
        league_id: int,
        season: int
    ) -> Dict:
        """Extract head-to-head features."""
        # Get last 5 H2H matches
        h2h_matches = self.db.query(Fixture).filter(
            and_(
                or_(
                    and_(
                        Fixture.home_team_id == home_team_id,
                        Fixture.away_team_id == away_team_id
                    ),
                    and_(
                        Fixture.home_team_id == away_team_id,
                        Fixture.away_team_id == home_team_id
                    )
                ),
                Fixture.league_id == league_id,
                Fixture.status.in_(["FT", "AET", "PEN"])
            )
        ).order_by(Fixture.match_date.desc()).limit(5).all()

        if not h2h_matches:
            return {
                "home_wins": 0, "draws": 0, "away_wins": 0,
                "home_goals_avg": 0.0, "away_goals_avg": 0.0,
                "total_matches": 0, "over_2_5_rate": 0.0,
                "btts_rate": 0.0, "home_win_rate": 0.0,
                "goals_per_match": 0.0
            }

        home_wins = 0
        draws = 0
        away_wins = 0
        home_goals = []
        away_goals = []
        over_2_5 = 0
        btts = 0

        for match in h2h_matches:
            if not match.score:
                continue

            # Determine which team was home in this match
            match_home_is_current_home = match.home_team_id == home_team_id

            h_goals = match.score.home_fulltime
            a_goals = match.score.away_fulltime

            if h_goals is not None and a_goals is not None:
                # Adjust perspective to current home/away
                if match_home_is_current_home:
                    home_goals.append(h_goals)
                    away_goals.append(a_goals)
                    if h_goals > a_goals:
                        home_wins += 1
                    elif h_goals < a_goals:
                        away_wins += 1
                    else:
                        draws += 1
                else:
                    home_goals.append(a_goals)
                    away_goals.append(h_goals)
                    if a_goals > h_goals:
                        home_wins += 1
                    elif a_goals < h_goals:
                        away_wins += 1
                    else:
                        draws += 1

                if (h_goals + a_goals) > 2.5:
                    over_2_5 += 1
                if h_goals > 0 and a_goals > 0:
                    btts += 1

        total = len(h2h_matches)

        return {
            "home_wins": home_wins,
            "draws": draws,
            "away_wins": away_wins,
            "home_goals_avg": np.mean(home_goals) if home_goals else 0.0,
            "away_goals_avg": np.mean(away_goals) if away_goals else 0.0,
            "total_matches": total,
            "over_2_5_rate": over_2_5 / total if total > 0 else 0.0,
            "btts_rate": btts / total if total > 0 else 0.0,
            "home_win_rate": home_wins / total if total > 0 else 0.0,
            "goals_per_match": np.mean([h + a for h, a in zip(home_goals, away_goals)]) if home_goals else 0.0
        }

    def _extract_league_features(self, league_id: int, season: int) -> Dict:
        """Extract league-level context features."""
        fixtures = self.db.query(Fixture).filter(
            and_(
                Fixture.league_id == league_id,
                Fixture.season == season,
                Fixture.status.in_(["FT", "AET", "PEN"])
            )
        ).all()

        if not fixtures:
            return {
                "avg_goals": 2.5,
                "avg_home_goals": 1.5,
                "avg_away_goals": 1.0,
                "home_win_rate": 0.45
            }

        total_goals = []
        home_goals = []
        away_goals = []
        home_wins = 0
        total_matches = 0

        for fixture in fixtures:
            if fixture.score and fixture.score.home_fulltime is not None and fixture.score.away_fulltime is not None:
                h = fixture.score.home_fulltime
                a = fixture.score.away_fulltime

                total_goals.append(h + a)
                home_goals.append(h)
                away_goals.append(a)

                if h > a:
                    home_wins += 1
                total_matches += 1

        return {
            "avg_goals": np.mean(total_goals) if total_goals else 2.5,
            "avg_home_goals": np.mean(home_goals) if home_goals else 1.5,
            "avg_away_goals": np.mean(away_goals) if away_goals else 1.0,
            "home_win_rate": home_wins / total_matches if total_matches > 0 else 0.45
        }

    def _get_elo_rating(self, team_id: int, league_id: int, season: int) -> float:
        """Get team's Elo rating."""
        rating = self.db.query(TeamRating).filter(
            and_(
                TeamRating.team_id == team_id,
                TeamRating.league_id == league_id,
                TeamRating.season == season
            )
        ).first()

        return rating.elo_rating if rating else 1500.0

    def _default_team_features(self) -> Dict:
        """Return default features when no data available."""
        return {
            "goals_scored_avg": 1.0,
            "goals_conceded_avg": 1.0,
            "goals_diff_avg": 0.0,
            "points_last_5": 5.0,
            "win_rate": 0.33,
            "draw_rate": 0.33,
            "loss_rate": 0.33,
            "shots_avg": 10.0,
            "shots_on_target_avg": 4.0,
            "possession_avg": 50.0,
            "xg_avg": 1.0,
            "xg_conceded_avg": 1.0,
            "corners_avg": 5.0,
            "fouls_avg": 12.0,
            "yellow_cards_avg": 2.0,
            "clean_sheets_rate": 0.25,
            "btts_rate": 0.5,
            "over_2_5_rate": 0.5,
            "first_half_goals_avg": 0.5,
            "second_half_goals_avg": 0.5,
            "form_trend": 1.0,
            "attack_strength": 1.0,
            "defense_strength": 1.0,
            "matches_played": 0
        }
