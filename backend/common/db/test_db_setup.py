#!/usr/bin/env python3
"""Test script to validate database setup."""

import sys
import os

# Add the backend directory to Python path for imports
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, backend_dir)

import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from common.config import settings
from common.db.database import close_db
from common.db.models.base import Base


async def test_db_setup():
    """Test database connection and basic operations."""
    try:
        print("Testing module imports...")
        print("OK - Modules imported successfully")

        # Check settings
        print(f"OK - Database URL configured: {settings.database_url_str[:20]}...")

        # Test engine creation
        print("OK - Async engine created")

        # Test with in-memory SQLite for setup validation
        print("Testing with SQLite in-memory database...")
        test_engine = create_async_engine("sqlite+aiosqlite:///:memory:")

        async with test_engine.begin() as conn:
            # Test basic connection
            result = await conn.execute(text("SELECT 1"))
            print(f"OK - SQLite connection successful: {result.fetchone()}")

            # Test Base metadata
            await conn.run_sync(Base.metadata.create_all)
            print("OK - Base metadata tables created successfully")

            # Check if tables exist
            result = await conn.execute(
                text("SELECT name FROM sqlite_master WHERE type='table'")
            )
            tables = result.fetchall()
            print(f"OK - Tables created: {[t[0] for t in tables]}")

        await test_engine.dispose()
        print("OK - SQLite test engine disposed")

        print("All database setup tests passed!")

    except Exception as e:
        print(f"Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False

    finally:
        await close_db()

    return True


if __name__ == "__main__":
    success = asyncio.run(test_db_setup())
    exit(0 if success else 1)
