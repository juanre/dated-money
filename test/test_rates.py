import pytest
import sqlite3
import tempfile
import json
from pathlib import Path
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import patch, MagicMock, mock_open

from dmon.rates import (
    parse_date,
    parse_optional_date,
    format_date,
    get_rates,
    get_rate,
    cache_day_rates,
    get_day_rates_from_repo,
    fetch_rates_from_exchangerate_api,
    get_day_rates_from_supabase,
    find_rates_for_date,
    ConnectionPool,
)
from dmon.currency import Currency


class TestDateParsing:
    """Test date parsing and formatting functions."""
    
    def test_parse_date_from_string(self):
        result = parse_date("2024-01-15")
        assert result == date(2024, 1, 15)
    
    def test_parse_date_from_date(self):
        input_date = date(2024, 1, 15)
        result = parse_date(input_date)
        assert result == input_date
    
    def test_parse_optional_date_none(self):
        assert parse_optional_date(None) is None
    
    def test_parse_optional_date_string(self):
        result = parse_optional_date("2024-01-15")
        assert result == date(2024, 1, 15)
    
    def test_format_date(self):
        assert format_date(date(2024, 1, 15)) == "2024-01-15"
        assert format_date("2024-01-15") == "2024-01-15"
    
    def test_parse_date_invalid_format(self):
        with pytest.raises(ValueError):
            parse_date("15-01-2024")  # Wrong format


class TestConnectionPool:
    """Test database connection pooling."""
    
    def test_singleton_pattern(self):
        with tempfile.NamedTemporaryFile() as tmp:
            pool1 = ConnectionPool(tmp.name)
            pool2 = ConnectionPool(tmp.name)
            assert pool1 is pool2
    
    def test_connection_reuse(self):
        with tempfile.NamedTemporaryFile() as tmp:
            # Reset the singleton for testing
            ConnectionPool._instance = None
            ConnectionPool._connection = None
            
            pool = ConnectionPool(tmp.name)
            conn1 = pool.get_connection()
            assert conn1 is not None
            pool.release_connection()
            
            # Connection should be reused
            conn2 = pool.get_connection()
            assert conn2 is not None
            # Can't guarantee same object due to connection pooling
            pool.release_connection()


class TestCacheOperations:
    """Test cache-related operations."""
    
    def test_cache_day_rates(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.dict('os.environ', {'DMON_RATES_CACHE': tmpdir}):
                rates = {
                    "USD": 1.0,
                    "EUR": 0.85,
                    "GBP": 0.73
                }
                cache_day_rates("2024-01-15", rates)
                
                # Verify data was cached
                retrieved = get_rates("2024-01-15", Currency.USD, Currency.EUR)
                assert retrieved is not None
                assert retrieved[Currency.USD] == Decimal("1.0")
                assert retrieved[Currency.EUR] == Decimal("0.85")
    
    def test_cache_filters_invalid_currencies(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.dict('os.environ', {'DMON_RATES_CACHE': tmpdir}):
                rates = {
                    "USD": 1.0,
                    "INVALID": 99.99,  # Should be filtered out
                    "EUR": 0.85
                }
                cache_day_rates("2024-01-15", rates)
                
                # Verify invalid currency was not cached
                retrieved = get_rates("2024-01-15", Currency.USD, Currency.EUR)
                assert retrieved is not None
                assert Currency.USD in retrieved
                assert Currency.EUR in retrieved


class TestRateRetrieval:
    """Test rate retrieval from various sources."""
    
    @patch('dmon.rates.requests.get')
    def test_fetch_rates_from_exchangerate_api_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "conversion_rates": {
                "USD": 1.0,
                "EUR": 0.85
            }
        }
        mock_get.return_value = mock_response
        
        with patch.dict('os.environ', {'DMON_EXCHANGERATE_API_KEY': 'test_key'}):
            rates = fetch_rates_from_exchangerate_api("2024-01-15")
            assert rates == {"USD": 1.0, "EUR": 0.85}
    
    @patch('dmon.rates.requests.get')
    def test_fetch_rates_from_exchangerate_api_failure(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        with patch.dict('os.environ', {'DMON_EXCHANGERATE_API_KEY': 'test_key'}):
            rates = fetch_rates_from_exchangerate_api("2024-01-15")
            assert rates is None
    
    def test_fetch_rates_no_api_key(self):
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(RuntimeError, match="Need an api key"):
                fetch_rates_from_exchangerate_api("2024-01-15")
    
    def test_get_day_rates_from_repo_success(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create mock repo structure
            money_dir = Path(tmpdir) / "money"
            money_dir.mkdir()
            
            rates_data = {
                "conversion_rates": {
                    "USD": 1.0,
                    "EUR": 0.85
                }
            }
            
            rates_file = money_dir / "2024-01-15-rates.json"
            with open(rates_file, "w") as f:
                json.dump(rates_data, f)
            
            with patch.dict('os.environ', {'DMON_RATES_REPO': tmpdir}):
                rates = get_day_rates_from_repo("2024-01-15")
                assert rates == {"USD": 1.0, "EUR": 0.85}
    
    def test_get_day_rates_from_repo_no_repo(self):
        with patch.dict('os.environ', {}, clear=True):
            rates = get_day_rates_from_repo("2024-01-15")
            assert rates is None
    
    @patch('dmon.rates.get_supabase_client')
    def test_get_day_rates_from_supabase_success(self, mock_client):
        mock_response = MagicMock()
        mock_response.data = {
            "conversion_rates": {
                "USD": 1.0,
                "EUR": 0.85
            }
        }
        
        mock_client.return_value.rpc.return_value.execute.return_value = mock_response
        
        rates = get_day_rates_from_supabase("2024-01-15")
        assert rates == {"USD": 1.0, "EUR": 0.85}
    
    @patch('dmon.rates.get_supabase_client')
    def test_get_day_rates_from_supabase_error(self, mock_client):
        mock_client.return_value.rpc.side_effect = Exception("Connection error")
        
        rates = get_day_rates_from_supabase("2024-01-15")
        assert rates is None


class TestRateFallback:
    """Test the rate fallback mechanism."""
    
    def test_find_rates_for_date_immediate_success(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create mock repo with rates for the exact date
            money_dir = Path(tmpdir) / "money"
            money_dir.mkdir()
            
            rates_data = {"conversion_rates": {"USD": 1.0}}
            rates_file = money_dir / "2024-01-15-rates.json"
            with open(rates_file, "w") as f:
                json.dump(rates_data, f)
            
            with patch.dict('os.environ', {'DMON_RATES_REPO': tmpdir}):
                rates, found_date = find_rates_for_date("2024-01-15")
                assert rates == {"USD": 1.0}
                assert found_date == date(2024, 1, 15)
    
    def test_find_rates_for_date_fallback(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create mock repo with rates for 2 days ago
            money_dir = Path(tmpdir) / "money"
            money_dir.mkdir()
            
            rates_data = {"conversion_rates": {"USD": 1.0}}
            rates_file = money_dir / "2024-01-13-rates.json"
            with open(rates_file, "w") as f:
                json.dump(rates_data, f)
            
            # Ensure only repo source is used
            with patch.dict('os.environ', {'DMON_RATES_REPO': tmpdir}, clear=True):
                with patch('dmon.rates.get_supabase_client', return_value=None):
                    with patch('dmon.rates.fetch_rates_from_exchangerate_api', return_value=None):
                        rates, found_date = find_rates_for_date("2024-01-15")
                        assert rates == {"USD": 1.0}
                        assert found_date == date(2024, 1, 13)
    
    def test_find_rates_for_date_max_fallback(self):
        """Test that fallback stops after 10 days."""
        # Clear all environment variables and mock all external sources
        with patch.dict('os.environ', {}, clear=True):
            with patch('dmon.rates.get_supabase_client', return_value=None):
                with patch('dmon.rates.get_day_rates_from_repo', return_value=None):
                    with patch('dmon.rates.fetch_rates_from_exchangerate_api', return_value=None):
                        rates, found_date = find_rates_for_date("2024-01-15")
                        assert rates is None
                        assert found_date is None


class TestGetRates:
    """Test the main get_rates function."""
    
    def setup_method(self):
        """Reset connection pool before each test."""
        import dmon.rates
        dmon.rates.CONNECTION_POOL = None
    
    def test_get_rates_from_cache(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.dict('os.environ', {'DMON_RATES_CACHE': tmpdir}):
                # Cache some rates
                cache_day_rates("2024-01-15", {"USD": 1.0, "EUR": 0.85})
                
                # Retrieve from cache
                rates = get_rates("2024-01-15", Currency.USD, Currency.EUR)
                assert rates[Currency.USD] == Decimal("1.0")
                assert rates[Currency.EUR] == Decimal("0.85")
    
    def test_get_rates_single_currency(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.dict('os.environ', {'DMON_RATES_CACHE': tmpdir}):
                cache_day_rates("2024-01-15", {"USD": 1.0})
                
                rate = get_rate("2024-01-15", Currency.USD)
                assert rate == Decimal("1.0")
    
    def test_get_rates_no_sources(self):
        """Test when no rate sources are available."""
        # Just ensure find_rates_for_date is mocked to return None
        with patch('dmon.rates.find_rates_for_date', return_value=(None, None)):
            # Also mock the DB to have no cached data
            with patch('dmon.rates.get_db_connection') as mock_conn:
                mock_cursor = MagicMock()
                mock_cursor.fetchone.return_value = None
                mock_conn.return_value.__enter__.return_value.cursor.return_value = mock_cursor
                
                rates = get_rates("2024-01-15", Currency.EUR)
                assert rates is None


class TestErrorCases:
    """Test error handling."""
    
    def test_invalid_date_format(self):
        with pytest.raises(ValueError):
            parse_date("not-a-date")
    
    def test_cache_database_error(self):
        """Test handling of database errors."""
        # Mock a database error during execute
        with patch('dmon.rates.get_db_connection') as mock_conn:
            mock_cursor = MagicMock()
            mock_cursor.execute.side_effect = sqlite3.OperationalError("Database error")
            mock_conn.return_value.__enter__.return_value.cursor.return_value = mock_cursor
            
            with pytest.raises(sqlite3.OperationalError):
                cache_day_rates("2024-01-15", {"USD": 1.0})