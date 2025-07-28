"""Test improved error handling for currency operations."""
import pytest
from dated_money.currency import to_currency_enum, Currency


def test_invalid_currency_code():
    """Test error message for invalid currency code."""
    with pytest.raises(ValueError, match="'XYZ' is not a valid currency code"):
        to_currency_enum('XYZ')
        
    with pytest.raises(ValueError, match="'INVALID' is not a valid currency code"):
        to_currency_enum('INVALID')


def test_invalid_currency_symbol():
    """Test error message for invalid currency symbol."""
    with pytest.raises(ValueError, match="'@' is not a recognized currency symbol"):
        to_currency_enum('@')


def test_invalid_type():
    """Test error message for invalid type."""
    with pytest.raises(TypeError, match="Expected Currency or str, got int"):
        to_currency_enum(123)
        
    with pytest.raises(TypeError, match="Expected Currency or str, got list"):
        to_currency_enum(['USD'])