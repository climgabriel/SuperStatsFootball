-- Add tier_required and priority columns to leagues table
-- Migration 003: Add leagues tier_required and priority columns

-- Add tier_required column if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'leagues' AND column_name = 'tier_required'
    ) THEN
        ALTER TABLE leagues ADD COLUMN tier_required VARCHAR(20) DEFAULT 'free';
        CREATE INDEX IF NOT EXISTS idx_leagues_tier_required ON leagues(tier_required);
        RAISE NOTICE 'Added tier_required column to leagues table';
    ELSE
        RAISE NOTICE 'tier_required column already exists';
    END IF;
END $$;

-- Add priority column if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'leagues' AND column_name = 'priority'
    ) THEN
        ALTER TABLE leagues ADD COLUMN priority INTEGER DEFAULT 0;
        CREATE INDEX IF NOT EXISTS idx_leagues_priority ON leagues(priority);
        RAISE NOTICE 'Added priority column to leagues table';
    ELSE
        RAISE NOTICE 'priority column already exists';
    END IF;
END $$;
