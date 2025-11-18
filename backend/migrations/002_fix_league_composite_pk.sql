-- Migration: Fix leagues table to use composite primary key (id, season)
-- Date: 2025-11-19
-- Description: Allow same league to exist across multiple seasons without conflicts

-- Step 1: Drop foreign key constraints that reference leagues.id
ALTER TABLE fixtures DROP CONSTRAINT IF EXISTS fixtures_league_id_fkey;
ALTER TABLE predictions DROP CONSTRAINT IF EXISTS predictions_league_id_fkey;

-- Step 2: Drop the existing primary key constraint
ALTER TABLE leagues DROP CONSTRAINT IF EXISTS leagues_pkey;

-- Step 3: Add composite primary key on (id, season)
-- This allows the same league ID to exist for different seasons
ALTER TABLE leagues ADD CONSTRAINT leagues_pkey PRIMARY KEY (id, season);

-- Step 4: Re-create foreign key constraints
-- Note: These still reference only league_id (not the composite key)
-- which is valid as long as the id exists in at least one (id, season) combination
ALTER TABLE fixtures
    ADD CONSTRAINT fixtures_league_id_fkey
    FOREIGN KEY (league_id)
    REFERENCES leagues(id)
    ON DELETE CASCADE;

ALTER TABLE predictions
    ADD CONSTRAINT predictions_league_id_fkey
    FOREIGN KEY (league_id)
    REFERENCES leagues(id)
    ON DELETE CASCADE;

-- Step 5: Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_leagues_id ON leagues(id);
CREATE INDEX IF NOT EXISTS idx_leagues_season ON leagues(season);
CREATE INDEX IF NOT EXISTS idx_leagues_is_active ON leagues(is_active);

-- Add comment
COMMENT ON TABLE leagues IS 'Stores league information from API-Football. Uses composite primary key (id, season) to support multiple seasons per league.';
