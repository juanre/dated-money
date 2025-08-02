# dated-money

A Python library for currency conversion with historical exchange rates.

## Overview

The library provides monetary values that combine:
- An amount (stored as Decimal, in cents)
- A currency (ISO 4217 code)
- An optional date for historical conversions

Exchange rates are fetched from multiple sources with automatic fallback.

## Installation

You can install `dated-money` using uv (recommended):

```bash
uv add dated-money
```

or pip:

```bash
pip install dated-money
```

### Development Installation

For development, clone the repository and install with development dependencies:

```bash
git clone https://github.com/juanre/dated-money
cd dated-money
uv sync
```

## Usage

### Basic Usage

```python
from dated_money import DM, DatedMoney, Currency

# Create factories using currency codes or symbols
Eur = DM('EUR', '2022-07-14')  # Using ISO code
Usd = DM('$', '2022-07-14')    # Using currency symbol
Gbp = DM('£', '2022-07-14')    # Common symbols: $, €, £, ¥, etc.

# All amounts created with Eur are in EUR base currency
price = Eur(100)  # €100
payment = Eur(50, Currency.USD)  # $50 converted to EUR (~€47)
fee = Eur(20, '£')  # £20 converted to EUR (~€23) - symbols work here too

# Addition is straightforward - all in EUR
total = price + payment + fee
assert total.currency == Currency.EUR

# Direct instantiation keeps original currency
usd_amount = DatedMoney(50, '$', '2022-07-14')  # Using symbol
gbp_amount = DatedMoney(20, 'GBP', '2022-07-14')  # Using ISO code

# Operations with DatedMoney instances
# Result is in the last operand's currency
result = usd_amount + gbp_amount  # Result in GBP
assert result.currency == Currency.GBP

# String representation and parsing
money = DatedMoney(100.50, 'EUR', '2022-07-14')
print(str(money))   # €100.50
print(repr(money))  # 2022-07-14 EUR 100.50

# Parse from string representation
parsed = DatedMoney.parse('2022-07-14 EUR 100.50')
assert parsed == money

# Parse without date
parsed_no_date = DatedMoney.parse('EUR 100.50')
assert parsed_no_date.currency == Currency.EUR
```

### API Reference

#### DM Factory Function

Creates a convenience function for instantiating monetary values with a default currency and date.

```python
DM(base_currency, base_date=None)
```

Parameters:
- `base_currency`: Default currency - accepts:
  - ISO code: 'EUR', 'USD', 'GBP' (case-insensitive)
  - Currency symbol: '$', '€', '£', '¥', etc.
  - Currency enum: Currency.EUR
- `base_date`: Default date for conversions (optional)

Returns a function that creates `DatedMoney` instances:

```python
# Various ways to create factories
Eur = DM('EUR', '2024-01-01')  # ISO code
Usd = DM('$', '2024-01-01')     # Symbol with date
Gbp = DM(Currency.GBP, '2024-01-01')  # Enum with date

# Create monetary values
price = Eur(100)  # €100
payment = Eur(50, 'USD')  # $50 → EUR
```

#### DatedMoney Class

Core class representing a monetary value.

```python
DatedMoney(amount, currency, on_date=None)
```

Parameters:
- `amount`: Numeric value or string. Append 'c' for cents (e.g., '1234c')
- `currency`: Accepts:
  - ISO code: 'EUR', 'USD', 'GBP' (case-insensitive)
  - Currency symbol: '$', '€', '£', '¥', etc.
  - Currency enum: Currency.EUR
- `on_date`: Date string 'YYYY-MM-DD' or date object (optional)

Methods:
- `cents(in_currency=None, on_date=None)`: Get amount in cents
- `amount(currency=None, rounding=False)`: Get decimal amount
- `to(currency, on_date=None)`: Convert to another currency
- `on(date)`: Create new instance with different date
- `parse(string)`: Parse from string representation (class method)

String representations:
- `str(money)`: Display format with symbol, e.g., "€100.50"
- `repr(money)`: Parseable format, e.g., "2022-07-14 EUR 100.50" or "EUR 100.50"

### Arithmetic Operations

- Addition/subtraction converts to the second operand's currency
- Multiplication/division with scalars preserves currency
- Division between DatedMoney instances returns a Decimal ratio
- Comparisons use the second operand's currency for conversion

```python
a = DatedMoney(100, 'EUR', '2024-01-01')
b = DatedMoney(50, 'USD', '2024-01-01')

# Result is in USD (second operand)
result = a + b  # Converts EUR to USD, adds
assert result.currency == Currency.USD

# Scalar operations
doubled = a * 2
assert doubled.cents() == 20000
assert doubled.currency == Currency.EUR
```

### Exchange Rate Sources

Rates are fetched in order:
1. Local SQLite cache
2. Git repository (if configured)
3. Supabase (if configured)
4. exchangerate-api.com

Missing rates trigger automatic fallback to previous dates (up to 10 days).

#### Environment Variables

- `DMON_RATES_CACHE`: Directory for the SQLite cache database (default: platform-specific cache directory - see below)

- `DMON_RATES_REPO`: Directory containing a git repository with exchange rates in a `money` subdirectory

- `SUPABASE_URL` and `SUPABASE_KEY`: Credentials for Supabase integration

- `DMON_EXCHANGERATE_API_KEY`: API key for exchangerate-api.com (required for historical rates on paid plans)

Rate files: `yyyy-mm-dd-rates.json` with structure:
```json
{"conversion_rates": {"USD": 1, "EUR": 0.85, ...}}
```

Cache locations:
- macOS: `~/Library/Caches/dated_money/exchange-rates.db`
- Linux: `~/.cache/dated_money/exchange-rates.db`
- Windows: `%LOCALAPPDATA%\dated_money\cache\exchange-rates.db`
- Override with `DMON_RATES_CACHE`

### Cache Management

```bash
# Create cache table
dmon-rates --create-table

# Fetch historical rates (requires paid API key)
dmon-rates --fetch-rates 2021-10-10:2021-10-20
```

## Development

This project uses:

- **uv** for package management
- **black** for code formatting
- **ruff** for linting
- **mypy** for type checking
- **pytest** for testing

### Running Tests

```bash
uv run pytest
```

### Code Quality

```bash
# Format code
uv run black src/ test/

# Run linter
uv run ruff check src/ test/

# Type checking
uv run mypy src/
```

## Backwards Compatibility

`Money` is maintained as an alias to `DM` for backwards compatibility.

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request on the [GitHub repository](https://github.com/juanre/dated-money).

## License

`dated-money` is released under the [MIT License](https://opensource.org/licenses/MIT).
