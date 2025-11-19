"""
Apply SQL migrations to the database.

This script reads and executes SQL migration files in order.
"""
import sys
import os
import psycopg2
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.config import settings


def apply_migrations():
    """Apply all SQL migrations in the migrations folder."""
    migrations_dir = Path(__file__).parent.parent / "migrations"

    print("=" * 80)
    print("Database Migration Tool")
    print("=" * 80)
    print(f"Migrations directory: {migrations_dir}")
    print(f"Database: {settings.DATABASE_URL[:50]}...")
    print("=" * 80)

    # Get all SQL migration files, sorted
    migration_files = sorted(migrations_dir.glob("*.sql"))
    migration_files = [f for f in migration_files if not f.name.endswith('.Identifier')]

    if not migration_files:
        print(" No migration files found!")
        return

    print(f"\nFound {len(migration_files)} migration file(s):")
    for mf in migration_files:
        print(f"  - {mf.name}")

    # Connect to database
    try:
        conn = psycopg2.connect(settings.DATABASE_URL)
        conn.autocommit = False
        cursor = conn.cursor()

        print("\n Database connected successfully!")

        for migration_file in migration_files:
            print(f"\n Applying migration: {migration_file.name}")

            with open(migration_file, 'r', encoding='utf-8') as f:
                sql = f.read()

            try:
                cursor.execute(sql)
                conn.commit()
                print(f"   {migration_file.name} applied successfully!")
            except Exception as e:
                print(f"   Error applying {migration_file.name}: {str(e)}")
                conn.rollback()
                # Continue with next migration

        cursor.close()
        conn.close()

        print("\n=" * 80)
        print(" Migration process completed!")
        print("=" * 80)

    except Exception as e:
        print(f"\n Database connection error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    apply_migrations()
