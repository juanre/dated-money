from datetime import date
from decimal import Decimal, InvalidOperation
from unittest.mock import patch

import pytest

from dated_money.currency import Currency
from dated_money.money import BaseMoney, Money, cents_str


class TestMoneyErrorCases:
    """Test error handling in Money classes."""

    def test_invalid_currency_string(self):
        """Test handling of invalid currency strings."""
        Eur = Money(Currency.EUR, "2024-01-15")

        with pytest.raises(ValueError):
            Eur(100, "INVALID")

    def test_currency_conversion_no_rates(self):
        """Test conversion when rates are not available."""
        Eur = Money(Currency.EUR, "2024-01-15")

        # Need to patch at the module where it's used, not where it's defined
        with patch("dated_money.money.get_rates") as mock_get_rates:
            mock_get_rates.return_value = None

            money = Eur(100)
            with pytest.raises(RuntimeError, match="Could not find exchange rates"):
                money.cents(Currency.USD)

    def test_currency_conversion_missing_rate(self):
        """Test conversion when specific currency rate is missing."""
        Eur = Money(Currency.EUR, "2024-01-15")

        with patch("dated_money.money.get_rates") as mock_get_rates:
            # USD rate is missing
            mock_get_rates.return_value = {Currency.EUR: Decimal("0.85"), Currency.USD: None}

            money = Eur(100)
            with pytest.raises(RuntimeError, match="is not available in the exchange rates"):
                money.cents(Currency.USD)

    def test_currency_conversion_source_rate_missing(self):
        """Test conversion when source currency rate is missing."""
        Eur = Money(Currency.EUR, "2024-01-15")

        with patch("dated_money.money.get_rates") as mock_get_rates:
            # EUR rate is missing
            mock_get_rates.return_value = {Currency.EUR: None, Currency.USD: Decimal("1.0")}

            money = Eur(100)
            with pytest.raises(RuntimeError, match="is not available in the exchange rates"):
                money.cents(Currency.USD)

    def test_invalid_date_string(self):
        """Test handling of invalid date strings."""
        Eur = Money(Currency.EUR, "2024-01-15")

        with pytest.raises(ValueError):
            Eur(100, on_date="not-a-date")

    def test_parse_invalid_string_format(self):
        """Test parsing of invalid string representations."""
        Eur = Money(Currency.EUR, "2024-01-15")
        # Test with wrong number of components (just one)
        with pytest.raises(ValueError, match="Cannot parse money string"):
            Eur.parse("single")

        # Test with invalid amount
        with pytest.raises((InvalidOperation, ValueError)):
            Eur.parse("EUR invalid_amount")

    def test_division_by_zero(self):
        """Test division by zero."""
        Eur = Money(Currency.EUR, "2024-01-15")
        money = Eur(100)

        with pytest.raises((InvalidOperation, ZeroDivisionError)):
            money / 0

    def test_invalid_cents_string(self):
        """Test handling of invalid cents string."""
        Eur = Money(Currency.EUR, "2024-01-15")

        # Empty string before 'c' causes error
        with pytest.raises(InvalidOperation):
            Eur("c")

        # Test with non-numeric cents
        with pytest.raises(InvalidOperation):
            Eur("abcc")

    def test_comparison_with_non_money(self):
        """Test comparison operations with non-Money objects."""
        Eur = Money(Currency.EUR, "2024-01-15")
        money = Eur(100)

        # Equality operations return NotImplemented, which Python converts
        assert (money == "not money") is False
        assert (money != "not money") is True

        # These raise AttributeError from normalized_amounts
        with pytest.raises(AttributeError):
            _ = money > "not money"

        with pytest.raises(AttributeError):
            _ = money < "not money"

        # These return NotImplemented which Python converts to TypeError
        with pytest.raises(TypeError):
            _ = money >= "not money"

        with pytest.raises(TypeError):
            _ = money <= "not money"

    def test_arithmetic_with_invalid_types(self):
        """Test arithmetic operations with invalid types."""
        Eur = Money(Currency.EUR, "2024-01-15")
        money = Eur(100)

        # String that can't be converted to number
        with pytest.raises((InvalidOperation, ValueError)):
            money + "not a number"

        with pytest.raises((InvalidOperation, ValueError)):
            money - "not a number"

        with pytest.raises((InvalidOperation, ValueError)):
            money * "not a number"


class TestMoneyEdgeCases:
    """Test edge cases in Money operations."""

    def test_very_large_amounts(self):
        """Test handling of very large monetary amounts."""
        Eur = Money(Currency.EUR, "2024-01-15")

        large_amount = "999999999999999999.99"
        money = Eur(large_amount)
        assert money.amount() == Decimal(large_amount)

    def test_very_small_amounts(self):
        """Test handling of very small monetary amounts."""
        Eur = Money(Currency.EUR, "2024-01-15")

        # Test sub-cent amounts
        money = Eur("0.001")  # 0.1 cent
        assert money.cents() == Decimal("0.1")

    def test_negative_amounts(self):
        """Test handling of negative amounts."""
        Eur = Money(Currency.EUR, "2024-01-15")

        money = Eur(-100)
        assert money.cents() == Decimal("-10000")
        assert str(money) == "€-100.00"

        # Test negation
        assert (-money).cents() == Decimal("10000")

    def test_precision_in_equality(self):
        """Test precision handling in equality comparisons."""
        # Create a money class with custom precision
        # Note: precision affects the instance, not the class
        Eur = Money(Currency.EUR, "2024-01-15")

        money1 = Eur("100.00")  # 100.00 EUR = 10000 cents
        money2 = Eur("100.01")  # 100.01 EUR = 10001 cents

        # By default (precision=0), these are not equal
        assert money1 != money2

    def test_currency_symbol_not_found(self):
        """Test handling when currency symbol is not in the dictionary."""
        # This is a hypothetical test - in practice all Currency enum values
        # should have symbols. But let's test the str() method behavior.
        Eur = Money(Currency.EUR, "2024-01-15")
        money = Eur(100)

        with patch("dated_money.money.CurrencySymbols", {}):
            # Should raise KeyError when symbol not found
            with pytest.raises(KeyError):
                str(money)

    @patch("dated_money.money.get_rates")
    def test_same_currency_conversion(self, mock_get_rates):
        """Test that same-currency conversion doesn't call get_rates."""
        Eur = Money(Currency.EUR, "2024-01-15")
        money = Eur(100)

        # Converting EUR to EUR should not call get_rates
        result = money.cents(Currency.EUR)
        assert result == Decimal("10000")
        mock_get_rates.assert_not_called()

    def test_money_factory_with_string_currency(self):
        """Test Money factory with string currency."""
        # Test with currency code
        Usd = Money("usd", "2024-01-15")
        assert Usd.base_currency == "usd"  # String is stored as-is

        # Test with Currency enum
        Gbp = Money(Currency.GBP, "2024-01-15")
        assert Gbp.base_currency == Currency.GBP

    def test_output_currency_override(self):
        """Test output currency override in display."""
        # Create money class that displays in USD regardless of actual currency
        EurInUsd = Money(Currency.EUR, "2024-01-15", output_currency=Currency.USD)

        with patch("dated_money.money.get_rates") as mock_get_rates:
            mock_get_rates.return_value = {
                Currency.EUR: Decimal("0.92"),  # 1 EUR = 0.92 (so 1 USD = ~1.087 EUR)
                Currency.USD: Decimal("1.0"),
            }

            money = EurInUsd(100, Currency.EUR)  # 100 EUR

            # Should display in USD (100 EUR / 0.92 = ~108.70 USD)
            result = str(money)
            assert "$" in result  # USD symbol
            assert "108.70" in result or "109" in result  # Allow for rounding


class TestCentsString:
    """Test the cents_str utility function."""

    def test_cents_str_with_decimal(self):
        assert cents_str(Decimal("1234.56")) == "1234.56c"

    def test_cents_str_with_int(self):
        assert cents_str(1234) == "1234c"

    def test_cents_str_with_float(self):
        assert cents_str(1234.56) == "1234.56c"

    def test_cents_str_with_string(self):
        assert cents_str("1234.56") == "1234.56c"
