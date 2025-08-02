"""Test database serialization of DatedMoney objects."""

import os
import sqlite3
import tempfile
from pathlib import Path

import pytest

from dated_money import DatedMoney, register_sqlite_converters
from dated_money.db_serialization import from_postgres, to_postgres

# Check if PostgreSQL is available
HAS_POSTGRES = False
# Uncomment to test skip behavior: HAS_POSTGRES = False
try:
    import os
    import subprocess

    import psycopg2

    # Check if PostgreSQL is running by trying to connect
    # First try with environment variables if set
    try:
        conn_params = {}
        if os.environ.get("PGHOST"):
            conn_params["host"] = os.environ["PGHOST"]
        if os.environ.get("PGPORT"):
            conn_params["port"] = os.environ["PGPORT"]
        if os.environ.get("PGUSER"):
            conn_params["user"] = os.environ["PGUSER"]
        if os.environ.get("PGPASSWORD"):
            conn_params["password"] = os.environ["PGPASSWORD"]

        # If no env vars, try default localhost connection
        if not conn_params:
            conn_params = {"host": "localhost"}

        # Try to connect with a short timeout
        conn = psycopg2.connect(**conn_params, connect_timeout=1, dbname="postgres")
        conn.close()
        HAS_POSTGRES = True
    except Exception:
        # Try to check if postgres is available via command line
        try:
            result = subprocess.run(["pg_isready"], capture_output=True, timeout=1)
            HAS_POSTGRES = result.returncode == 0
        except Exception:
            HAS_POSTGRES = False
except ImportError:
    # psycopg2 is not installed
    HAS_POSTGRES = False


class TestSQLiteSerialization:
    """Test SQLite serialization and deserialization."""

    def test_conform_method(self):
        """Test that __conform__ correctly serializes to string."""
        money = DatedMoney(100.50, "EUR", "2024-01-01")

        # Test the __conform__ method directly
        result = money.__conform__(sqlite3.PrepareProtocol)
        assert result == "2024-01-01 EUR 100.50"

        # Test with no date
        money_no_date = DatedMoney(50, "USD")
        result_no_date = money_no_date.__conform__(sqlite3.PrepareProtocol)
        assert result_no_date == "USD 50.00"

    def test_basic_sqlite_storage(self):
        """Test storing DatedMoney in SQLite without converters."""
        money = DatedMoney(100.50, "EUR", "2024-01-01")

        with sqlite3.connect(":memory:") as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE test (
                    id INTEGER PRIMARY KEY,
                    amount TEXT
                )
            """
            )

            # SQLite automatically calls __conform__
            cursor.execute("INSERT INTO test (amount) VALUES (?)", (money,))

            cursor.execute("SELECT amount FROM test")
            stored_value = cursor.fetchone()[0]

            assert stored_value == "2024-01-01 EUR 100.50"

    def test_sqlite_with_converters(self):
        """Test automatic conversion with registered converters."""
        # Register converters
        register_sqlite_converters()

        money1 = DatedMoney(100.50, "EUR", "2024-01-01")
        money2 = DatedMoney("5000c", "GBP")  # 50.00 GBP from cents

        with sqlite3.connect(":memory:", detect_types=sqlite3.PARSE_DECLTYPES) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE transactions (
                    id INTEGER PRIMARY KEY,
                    amount DATEDMONEY,
                    description TEXT
                )
            """
            )

            # Insert multiple records
            cursor.execute(
                "INSERT INTO transactions (amount, description) VALUES (?, ?)",
                (money1, "Payment 1"),
            )
            cursor.execute(
                "INSERT INTO transactions (amount, description) VALUES (?, ?)",
                (money2, "Payment 2"),
            )

            # Retrieve and verify automatic conversion
            cursor.execute("SELECT amount, description FROM transactions ORDER BY id")
            rows = cursor.fetchall()

            # First record
            retrieved1 = rows[0][0]
            assert isinstance(retrieved1, DatedMoney)
            assert retrieved1.amount() == money1.amount()
            assert retrieved1.currency == money1.currency
            assert retrieved1.on_date == money1.on_date

            # Second record
            retrieved2 = rows[1][0]
            assert isinstance(retrieved2, DatedMoney)
            assert retrieved2.amount() == money2.amount()
            assert retrieved2.currency == money2.currency
            assert retrieved2.on_date is None

    def test_operations_on_retrieved_objects(self):
        """Test that retrieved objects work correctly."""
        register_sqlite_converters()
        money = DatedMoney(100, "EUR", "2022-07-14")

        with sqlite3.connect(":memory:", detect_types=sqlite3.PARSE_DECLTYPES) as conn:
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE test (amount DATEDMONEY)")
            cursor.execute("INSERT INTO test VALUES (?)", (money,))

            cursor.execute("SELECT amount FROM test")
            retrieved = cursor.fetchone()[0]

            # Test arithmetic operations
            doubled = retrieved * 2
            assert doubled.amount() == 200
            assert doubled.currency == money.currency

            # Test currency conversion
            usd_amount = retrieved.to("USD")
            assert usd_amount.currency.value == "usd"

            # Test comparison
            assert retrieved == money

    def test_null_values(self):
        """Test handling of NULL values."""
        register_sqlite_converters()

        with sqlite3.connect(":memory:", detect_types=sqlite3.PARSE_DECLTYPES) as conn:
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE test (amount DATEDMONEY)")
            cursor.execute("INSERT INTO test VALUES (?)", (None,))

            cursor.execute("SELECT amount FROM test")
            result = cursor.fetchone()[0]
            assert result is None

    def test_persistent_database(self):
        """Test with a persistent database file."""
        register_sqlite_converters()
        money = DatedMoney(250.75, "JPY", "2024-03-15")

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"

            # Write to database
            with sqlite3.connect(str(db_path), detect_types=sqlite3.PARSE_DECLTYPES) as conn:
                cursor = conn.cursor()
                cursor.execute("CREATE TABLE test (amount DATEDMONEY)")
                cursor.execute("INSERT INTO test VALUES (?)", (money,))

            # Read from database in new connection
            with sqlite3.connect(str(db_path), detect_types=sqlite3.PARSE_DECLTYPES) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT amount FROM test")
                retrieved = cursor.fetchone()[0]

                assert isinstance(retrieved, DatedMoney)
                assert retrieved == money


@pytest.mark.skipif(not HAS_POSTGRES, reason="PostgreSQL not available")
class TestPostgreSQLSerialization:
    """Test PostgreSQL serialization functions."""

    def test_to_postgres(self):
        """Test conversion to PostgreSQL format."""
        money1 = DatedMoney(100.50, "EUR", "2024-01-01")
        assert to_postgres(money1) == "2024-01-01 EUR 100.50"

        money2 = DatedMoney(50, "USD")
        assert to_postgres(money2) == "USD 50.00"

    def test_from_postgres(self):
        """Test conversion from PostgreSQL format."""
        # With date
        money1 = from_postgres("2024-01-01 EUR 100.50")
        assert isinstance(money1, DatedMoney)
        assert money1.amount() == 100.50
        assert money1.currency.value == "eur"
        assert str(money1.on_date) == "2024-01-01"

        # Without date
        money2 = from_postgres("USD 50.00")
        assert isinstance(money2, DatedMoney)
        assert money2.amount() == 50.00
        assert money2.currency.value == "usd"
        assert money2.on_date is None

        # None value
        assert from_postgres(None) is None

    def test_postgres_roundtrip(self):
        """Test that to_postgres and from_postgres are inverse operations."""
        original = DatedMoney(123.45, "GBP", "2024-02-29")
        serialized = to_postgres(original)
        deserialized = from_postgres(serialized)

        assert deserialized == original
        assert deserialized.currency == original.currency
        assert deserialized.on_date == original.on_date

    def test_postgres_integration(self):
        """Test actual PostgreSQL integration if database is available."""
        import psycopg2
        from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

        try:
            # Connect to PostgreSQL
            conn = psycopg2.connect(dbname="postgres", host="localhost")
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()

            # Create a test database
            test_db_name = "test_datedmoney_" + str(os.getpid())
            try:
                cursor.execute(f"CREATE DATABASE {test_db_name}")

                # Connect to the test database
                conn.close()
                conn = psycopg2.connect(dbname=test_db_name, host="localhost")
                cursor = conn.cursor()

                # Create table
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS transactions (
                        id SERIAL PRIMARY KEY,
                        amount TEXT,
                        description TEXT
                    )
                """
                )
                conn.commit()

                # Test inserting DatedMoney
                money1 = DatedMoney(100.50, "EUR", "2024-01-01")
                money2 = DatedMoney(75.25, "USD")

                cursor.execute(
                    "INSERT INTO transactions (amount, description) VALUES (%s, %s), (%s, %s)",
                    (to_postgres(money1), "Test 1", to_postgres(money2), "Test 2"),
                )
                conn.commit()

                # Retrieve and verify
                cursor.execute("SELECT id, amount, description FROM transactions ORDER BY id")
                rows = cursor.fetchall()

                assert len(rows) == 2

                # Check first record
                retrieved1 = from_postgres(rows[0][1])
                assert retrieved1 == money1
                assert rows[0][2] == "Test 1"

                # Check second record
                retrieved2 = from_postgres(rows[1][1])
                assert retrieved2 == money2
                assert rows[1][2] == "Test 2"

            finally:
                # Clean up
                conn.close()
                # Drop test database
                cleanup_conn = psycopg2.connect(dbname="postgres", host="localhost")
                cleanup_conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
                cleanup_cursor = cleanup_conn.cursor()
                cleanup_cursor.execute(f"DROP DATABASE IF EXISTS {test_db_name}")
                cleanup_conn.close()

        except psycopg2.OperationalError:
            pytest.skip("Cannot connect to PostgreSQL for integration test")


class TestEdgeCases:
    """Test edge cases for database serialization."""

    def test_special_amounts(self):
        """Test serialization of special amount values."""
        register_sqlite_converters()

        test_cases = [
            DatedMoney(0, "EUR"),  # Zero
            DatedMoney(-100, "USD"),  # Negative
            DatedMoney("1c", "GBP"),  # One cent
            DatedMoney(999999.99, "JPY"),  # Large amount
        ]

        with sqlite3.connect(":memory:", detect_types=sqlite3.PARSE_DECLTYPES) as conn:
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE test (amount DATEDMONEY)")

            for money in test_cases:
                cursor.execute("INSERT INTO test VALUES (?)", (money,))

            cursor.execute("SELECT amount FROM test")
            retrieved = [row[0] for row in cursor.fetchall()]

            for original, retrieved_money in zip(test_cases, retrieved):
                assert retrieved_money == original

    def test_parse_invalid_format(self):
        """Test handling of invalid stored formats."""
        register_sqlite_converters()

        with sqlite3.connect(":memory:", detect_types=sqlite3.PARSE_DECLTYPES) as conn:
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE test (amount DATEDMONEY)")

            # Manually insert invalid format
            cursor.execute("INSERT INTO test VALUES (?)", ("invalid format",))

            cursor.execute("SELECT amount FROM test")
            with pytest.raises(ValueError):
                cursor.fetchone()
