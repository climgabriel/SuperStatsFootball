"""
Create database tables using SQL DDL.

This script creates all necessary tables for the SuperStatsFootball application.
"""
import sys
import os
import psycopg2

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.config import settings


CREATE_TABLES_SQL = """
-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(36) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    tier VARCHAR(20) DEFAULT 'free' NOT NULL,
    subscription_id VARCHAR(255),
    subscription_status VARCHAR(20) DEFAULT 'active',
    stripe_customer_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_tier ON users(tier);

-- Create teams table
CREATE TABLE IF NOT EXISTS teams (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(10),
    country VARCHAR(100),
    founded INTEGER,
    logo VARCHAR(500),
    venue_name VARCHAR(255),
    venue_city VARCHAR(100),
    venue_capacity INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_teams_name ON teams(name);
CREATE INDEX IF NOT EXISTS idx_teams_country ON teams(country);

-- Create leagues table with simple primary key (id only)
-- We'll use a unique constraint on (id, season) instead of composite PK
CREATE TABLE IF NOT EXISTS leagues (
    id INTEGER PRIMARY KEY,
    season INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    country VARCHAR(100),
    logo VARCHAR(500),
    type VARCHAR(50),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_leagues_id_season ON leagues(id, season);
CREATE INDEX IF NOT EXISTS idx_leagues_season ON leagues(season);
CREATE INDEX IF NOT EXISTS idx_leagues_is_active ON leagues(is_active);

-- Create fixtures table
CREATE TABLE IF NOT EXISTS fixtures (
    id INTEGER PRIMARY KEY,
    league_id INTEGER,
    season INTEGER NOT NULL,
    round VARCHAR(50),
    match_date TIMESTAMP NOT NULL,
    timestamp BIGINT NOT NULL,
    home_team_id INTEGER,
    away_team_id INTEGER,
    status VARCHAR(20),
    elapsed_time INTEGER,
    venue VARCHAR(255),
    referee VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (league_id) REFERENCES leagues(id) ON DELETE CASCADE,
    FOREIGN KEY (home_team_id) REFERENCES teams(id) ON DELETE CASCADE,
    FOREIGN KEY (away_team_id) REFERENCES teams(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_fixtures_league_id ON fixtures(league_id);
CREATE INDEX IF NOT EXISTS idx_fixtures_season ON fixtures(season);
CREATE INDEX IF NOT EXISTS idx_fixtures_match_date ON fixtures(match_date);
CREATE INDEX IF NOT EXISTS idx_fixtures_status ON fixtures(status);
CREATE INDEX IF NOT EXISTS idx_fixtures_home_team ON fixtures(home_team_id);
CREATE INDEX IF NOT EXISTS idx_fixtures_away_team ON fixtures(away_team_id);

-- Create fixture_scores table
CREATE TABLE IF NOT EXISTS fixture_scores (
    id VARCHAR(36) PRIMARY KEY,
    fixture_id INTEGER NOT NULL,
    halftime_home INTEGER,
    halftime_away INTEGER,
    fulltime_home INTEGER,
    fulltime_away INTEGER,
    extratime_home INTEGER,
    extratime_away INTEGER,
    penalty_home INTEGER,
    penalty_away INTEGER,
    FOREIGN KEY (fixture_id) REFERENCES fixtures(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_fixture_scores_fixture_id ON fixture_scores(fixture_id);

-- Create fixture_stats table
CREATE TABLE IF NOT EXISTS fixture_stats (
    id VARCHAR(36) PRIMARY KEY,
    fixture_id INTEGER NOT NULL,
    team_id INTEGER NOT NULL,
    shots_on_goal INTEGER,
    shots_off_goal INTEGER,
    total_shots INTEGER,
    blocked_shots INTEGER,
    shots_inside_box INTEGER,
    shots_outside_box INTEGER,
    fouls INTEGER,
    corner_kicks INTEGER,
    offsides INTEGER,
    ball_possession INTEGER,
    yellow_cards INTEGER,
    red_cards INTEGER,
    goalkeeper_saves INTEGER,
    total_passes INTEGER,
    passes_accurate INTEGER,
    passes_percent INTEGER,
    expected_goals FLOAT,
    goals_prevented FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (fixture_id) REFERENCES fixtures(id) ON DELETE CASCADE,
    FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_fixture_stats_fixture_id ON fixture_stats(fixture_id);
CREATE INDEX IF NOT EXISTS idx_fixture_stats_team_id ON fixture_stats(team_id);

-- Create fixture_odds table
CREATE TABLE IF NOT EXISTS fixture_odds (
    id VARCHAR(36) PRIMARY KEY,
    fixture_id INTEGER NOT NULL,
    bookmaker_id INTEGER NOT NULL,
    bookmaker_name VARCHAR(100) NOT NULL,

    -- 1X2 Full Time Odds
    home_win_odds FLOAT,
    draw_odds FLOAT,
    away_win_odds FLOAT,

    -- Halftime Odds
    ht_home_win_odds FLOAT,
    ht_draw_odds FLOAT,
    ht_away_win_odds FLOAT,

    -- Fulltime Odds
    ft_home_win_odds FLOAT,
    ft_draw_odds FLOAT,
    ft_away_win_odds FLOAT,

    -- Over/Under 2.5 Goals
    over_2_5_odds FLOAT,
    under_2_5_odds FLOAT,

    -- Metadata
    is_live BOOLEAN DEFAULT FALSE NOT NULL,
    fetched_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (fixture_id) REFERENCES fixtures(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_fixture_odds_fixture_id ON fixture_odds(fixture_id);
CREATE INDEX IF NOT EXISTS idx_fixture_odds_bookmaker_name ON fixture_odds(bookmaker_name);
CREATE INDEX IF NOT EXISTS idx_fixture_odds_is_live ON fixture_odds(is_live);
CREATE INDEX IF NOT EXISTS idx_fixture_odds_composite ON fixture_odds(fixture_id, bookmaker_name, is_live);

-- Create predictions table
CREATE TABLE IF NOT EXISTS predictions (
    id VARCHAR(36) PRIMARY KEY,
    fixture_id INTEGER NOT NULL,
    league_id INTEGER,
    home_team_id INTEGER,
    away_team_id INTEGER,
    tier VARCHAR(20) NOT NULL,
    prediction_type VARCHAR(50) NOT NULL,
    home_win_probability FLOAT,
    draw_probability FLOAT,
    away_win_probability FLOAT,
    predicted_home_goals FLOAT,
    predicted_away_goals FLOAT,
    predicted_total_goals FLOAT,
    over_under_2_5 VARCHAR(10),
    both_teams_score VARCHAR(10),
    confidence_score FLOAT,
    model_versions JSONB,
    statistical_models JSONB,
    ml_models JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (fixture_id) REFERENCES fixtures(id) ON DELETE CASCADE,
    FOREIGN KEY (league_id) REFERENCES leagues(id) ON DELETE CASCADE,
    FOREIGN KEY (home_team_id) REFERENCES teams(id) ON DELETE CASCADE,
    FOREIGN KEY (away_team_id) REFERENCES teams(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_predictions_fixture_id ON predictions(fixture_id);
CREATE INDEX IF NOT EXISTS idx_predictions_tier ON predictions(tier);
CREATE INDEX IF NOT EXISTS idx_predictions_prediction_type ON predictions(prediction_type);
CREATE INDEX IF NOT EXISTS idx_predictions_league_id ON predictions(league_id);
"""


def create_tables():
    """Create all database tables."""
    print("=" * 80)
    print("Creating Database Tables")
    print("=" * 80)
    print(f"Database: {settings.DATABASE_URL[:50]}...")
    print("=" * 80)

    try:
        conn = psycopg2.connect(settings.DATABASE_URL)
        conn.autocommit = True
        cursor = conn.cursor()

        print("\n Database connected successfully!")
        print("\n Creating tables...")

        cursor.execute(CREATE_TABLES_SQL)

        print(" All tables created successfully!")

        # Show created tables
        cursor.execute("""
            SELECT tablename
            FROM pg_tables
            WHERE schemaname = 'public'
            ORDER BY tablename;
        """)

        tables = cursor.fetchall()
        print(f"\n Created {len(tables)} table(s):")
        for table in tables:
            print(f"  - {table[0]}")

        cursor.close()
        conn.close()

        print("\n=" * 80)
        print(" Database initialization completed!")
        print("=" * 80)

    except Exception as e:
        print(f"\n Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    create_tables()
