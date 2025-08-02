import os
import shutil
from pathlib import Path

import pytest


@pytest.fixture(autouse=True, scope="session")
def setup_test_database():
    """Copy the original database to a test version before running tests."""
    test_dir = Path("test/res")
    test_cache_dir = Path("test/test_cache")
    original_db = test_dir / "exchange-rates.db"
    test_db = test_cache_dir / "exchange-rates.db"

    # Create test cache directory
    test_cache_dir.mkdir(exist_ok=True)

    # Copy the original database to test cache
    if original_db.exists():
        shutil.copy2(original_db, test_db)

    yield

    # Cleanup is optional - we keep the test db for inspection if needed


@pytest.fixture(autouse=True)
def env_setup(monkeypatch):
    monkeypatch.setenv("DMON_RATES_REPO", "test/res")
    # Use the test cache directory
    monkeypatch.setenv("DMON_RATES_CACHE", "test/test_cache")
