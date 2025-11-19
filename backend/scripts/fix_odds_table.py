"""
Fix odds table naming issue.

This script drops the incorrect 'odds' table and creates the correct 'fixture_odds' table.
"""
import sys
import os
import psycopg2

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.config import settings


FIX_ODDS_TABLE_SQL = """
-- Drop the incorrect 'odds' table
DROP TABLE IF EXISTS odds CASCADE;

-- Create the correct fixture_odds table
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
"""


def fix_odds_table():
    """Fix odds table naming."""
    print("=" * 80)
    print("Fixing Odds Table Naming Issue")
    print("=" * 80)
    print(f"Database: {settings.DATABASE_URL[:50]}...")
    print("=" * 80)

    try:
        conn = psycopg2.connect(settings.DATABASE_URL)
        conn.autocommit = True
        cursor = conn.cursor()

        print("\n Database connected successfully!")
        print("\n Dropping 'odds' table and creating 'fixture_odds' table...")

        cursor.execute(FIX_ODDS_TABLE_SQL)

        print(" Tables fixed successfully!")

        # Show all tables
        cursor.execute("""
            SELECT tablename
            FROM pg_tables
            WHERE schemaname = 'public'
            ORDER BY tablename;
        """)

        tables = cursor.fetchall()
        print(f"\n Current tables in database:")
        for table in tables:
            print(f"  - {table[0]}")

        cursor.close()
        conn.close()

        print("\n=" * 80)
        print(" Odds table fix completed!")
        print("=" * 80)

    except Exception as e:
        print(f"\n Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    fix_odds_table()
