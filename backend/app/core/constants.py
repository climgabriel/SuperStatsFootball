"""
Application-wide constants for SuperStatsFootball.

This module contains all magic numbers and default values used throughout
the application, organized by category for easy maintenance.
"""

# ==============================================================================
# QUERY DEFAULTS
# ==============================================================================

# Pagination
DEFAULT_LIMIT = 50
MAX_LIMIT = 200
DEFAULT_OFFSET = 0

# Time windows
DEFAULT_DAYS_AHEAD = 7
MIN_DAYS_AHEAD = 1
MAX_DAYS_AHEAD = 30


# ==============================================================================
# STATISTICAL DEFAULTS (when no historical data is available)
# ==============================================================================

# Expected Goals (xG)
DEFAULT_HOME_XG = 1.5
DEFAULT_AWAY_XG = 1.2

# Corners
DEFAULT_HOME_CORNERS = 6.0
DEFAULT_AWAY_CORNERS = 4.5

# Cards
DEFAULT_HOME_YELLOW_CARDS = 2.1
DEFAULT_AWAY_YELLOW_CARDS = 1.9
DEFAULT_HOME_RED_CARDS = 0.1
DEFAULT_AWAY_RED_CARDS = 0.1

# Shots
DEFAULT_HOME_TOTAL_SHOTS = 12.5
DEFAULT_AWAY_TOTAL_SHOTS = 9.8
DEFAULT_HOME_SHOTS_ON_GOAL = 5.2
DEFAULT_AWAY_SHOTS_ON_GOAL = 4.1

# Fouls
DEFAULT_HOME_FOULS = 11.2
DEFAULT_AWAY_FOULS = 12.3

# Offsides
DEFAULT_HOME_OFFSIDES = 2.3
DEFAULT_AWAY_OFFSIDES = 1.9
DEFAULT_HOME_SHOTS_FOR_TACTICAL = 12.0
DEFAULT_AWAY_SHOTS_FOR_TACTICAL = 10.0

# Offside tactical threshold
OFFSIDES_HIGH_LINE_THRESHOLD = 2.0


# ==============================================================================
# RATING SYSTEM DEFAULTS
# ==============================================================================

# ELO Rating
DEFAULT_ELO_RATING = 1500.0
ELO_K_FACTOR = 32

# Glicko Rating
DEFAULT_GLICKO_RATING = 1500.0
DEFAULT_GLICKO_RD = 350.0

# Dixon-Coles
DEFAULT_HOME_ADVANTAGE = 0.3
DEFAULT_OFFENSIVE_STRENGTH = 1.0
DEFAULT_DEFENSIVE_STRENGTH = 1.0


# ==============================================================================
# FIXTURE STATUS CODES
# ==============================================================================

FIXTURE_STATUS_NOT_STARTED = "NS"
FIXTURE_STATUS_TO_BE_DECIDED = "TBD"
FIXTURE_STATUS_LIVE = "LIVE"
FIXTURE_STATUS_FINISHED = "FT"
FIXTURE_STATUS_HALFTIME = "HT"
FIXTURE_STATUS_POSTPONED = "PST"
FIXTURE_STATUS_CANCELLED = "CANC"
FIXTURE_STATUS_ABANDONED = "ABD"

# Common upcoming fixture statuses
UPCOMING_FIXTURE_STATUSES = [FIXTURE_STATUS_NOT_STARTED, FIXTURE_STATUS_TO_BE_DECIDED]


# ==============================================================================
# ODDS AND PROBABILITIES (for display purposes)
# ==============================================================================

# These are sample/placeholder values - in production, use real odds calculation
SAMPLE_ODDS = {
    "over_under_2_5": {
        "over": {"odds": "1.85", "probability": "54.2%"},
        "under": {"odds": "1.95", "probability": "45.8%"}
    },
    "over_under_1_5": {
        "over": {"odds": "1.25", "probability": "78.5%"},
        "under": {"odds": "3.75", "probability": "21.5%"}
    },
    "over_under_3_5": {
        "over": {"odds": "2.50", "probability": "38.2%"},
        "under": {"odds": "1.50", "probability": "61.8%"}
    },
    "btts": {
        "yes": {"odds": "1.65", "probability": "62.5%"},
        "no": {"odds": "2.20", "probability": "37.5%"}
    },
    "corners": {
        "over_9_5": {"odds": "1.90", "probability": "52.6%"},
        "over_10_5": {"odds": "2.10", "probability": "47.6%"},
        "over_11_5": {"odds": "2.50", "probability": "40.0%"},
        "home_over_5_5": {"odds": "1.75", "probability": "57.1%"},
        "away_over_4_5": {"odds": "2.00", "probability": "50.0%"}
    },
    "cards": {
        "over_3_5": {"odds": "1.90", "probability": "52.6%"},
        "over_4_5": {"odds": "2.30", "probability": "43.5%"}
    },
    "shots": {
        "over_20_5": {"odds": "1.85", "probability": "54.1%"},
        "over_22_5": {"odds": "2.10", "probability": "47.6%"}
    },
    "fouls": {
        "over_22_5": {"odds": "1.90", "probability": "52.6%"},
        "over_24_5": {"odds": "2.20", "probability": "45.5%"}
    },
    "offsides": {
        "over_3_5": {"odds": "1.95", "probability": "51.3%"},
        "over_4_5": {"odds": "2.40", "probability": "41.7%"}
    }
}


# ==============================================================================
# CALCULATION CONSTANTS
# ==============================================================================

# Minimum sample size for statistical calculations
MIN_SAMPLE_SIZE = 1

# Discipline index divisor (used in fouls calculations)
DISCIPLINE_INDEX_DIVISOR = 4

# Tactical index multiplier (used in offsides calculations)
TACTICAL_INDEX_MULTIPLIER = 3
