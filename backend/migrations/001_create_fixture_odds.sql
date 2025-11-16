-- Migration: Create fixture_odds table for storing Superbet.ro odds
-- Date: 2025-11-14
-- Description: Add support for bookmaker odds (1X2, HT/FT, Over/Under 2.5)

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

    -- Foreign key constraint
    FOREIGN KEY (fixture_id) REFERENCES fixtures(id) ON DELETE CASCADE
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_fixture_odds_fixture_id ON fixture_odds(fixture_id);
CREATE INDEX IF NOT EXISTS idx_fixture_odds_bookmaker_name ON fixture_odds(bookmaker_name);
CREATE INDEX IF NOT EXISTS idx_fixture_odds_is_live ON fixture_odds(is_live);
CREATE INDEX IF NOT EXISTS idx_fixture_odds_composite ON fixture_odds(fixture_id, bookmaker_name, is_live);

-- Add comment
COMMENT ON TABLE fixture_odds IS 'Stores bookmaker odds from Superbet.ro for fixtures. Supports 1X2, Halftime/Fulltime, and Over/Under 2.5 goals.';
