# Changelog

All notable changes to the dated-money project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.0] - 2025-08-01

### ⚠️ BREAKING CHANGES

**Complete architectural overhaul from class factory to function factory pattern:**

- **`Money()` now returns a function, not a class**
  - Old: `Eur = Money(Currency.EUR); price = Eur(100)` (created a class)
  - New: `Eur = DM('EUR'); price = Eur(100)` (creates instances via function)

- **New primary API: `DM()` function factory**
  - `DM(base_currency, base_date=None)` returns a function for creating monetary values
  - `Money` is now an alias to `DM` for backwards compatibility

- **Replaced `BaseMoney` class with `DatedMoney` class**
  - Direct instantiation: `DatedMoney(amount, currency, on_date)`
  - No more dynamic class creation with type()
  - No more class-level attributes (base_currency, base_date, output_currency)

- **Currency handling changes**
  - Constructor now requires explicit `currency` parameter (was `display_currency`)
  - Each instance stores its own currency and date (not class-level)
  - Removed `base_currency` class attribute

- **Arithmetic operation behavior changes**
  - Operations now return results in the **second operand's currency** (was base currency)
  - Old: `eur + usd` → EUR (base currency)
  - New: `eur + usd` → USD (second operand's currency)
  - Date handling: result uses the second operand's date

- **Method signature changes**
  - `cents()` now accepts optional `on_date` parameter
  - `parse_optional_date()` now accepts `defaults_to` parameter
  - `normalized_amounts()` now converts to the other operand's currency (not base)

### Added
- `DM()` function factory as the primary API
- `DatedMoney` class for direct instantiation
- `cents_str()` now handles strings already ending with 'c'
- Copyright headers to all source files
- `on_date` parameter to `cents()` method for flexible date conversion

### Changed
- Simplified architecture: function factory instead of class factory
- `Money()` is now an alias to `DM()` for backwards compatibility

### Removed
- `BaseMoney` class (replaced by `DatedMoney`)
- Dynamic class creation with `type()`
- `class_name` parameter from Money factory
- `output_currency` parameter from Money factory
- Class-level attributes (base_currency, base_date)
- Complex normalization to base currency in operations

### Documentation
- Removed obsolete documentation files using old architecture
- Removed examples directory with outdated code

## Migration Guide from 2.0 to 2.1

### Update your factory usage:
```python
# Old (2.0) - Class factory
Eur = Money(Currency.EUR, '2024-01-01')  # Returns a class
price = Eur(100)  # Instantiate the class

# New (2.1) - Function factory
Eur = DM('EUR', '2024-01-01')  # Returns a function; Money remains as an alias of DM
price = Eur(100)  # Call the function
```

### Direct instantiation:
```python
price = DatedMoney(100, 'EUR', '2024-01-01')
```

### Arithmetic operations:
```python
# Be aware of the new behavior
eur = DatedMoney(100, 'EUR')
usd = DatedMoney(50, 'USD')

# Old: result in base currency (EUR)
# New: result in second operand's currency (USD)
result = eur + usd  # Result is in USD
```

## [2.0.0] - 2024-01-28

### ⚠️ BREAKING CHANGES
- **Module renamed from `dmon` to `dated_money`**
  - All imports must be updated: `from dmon import ...` → `from dated_money import ...`
  - The Python module name is now self-documenting and clearer
  - CLI command `dmon-rates` remains unchanged
  - Removed the `dmon` CLI command (it served no useful purpose)

### Added
- Comprehensive logging infrastructure with configurable logger
- Extensive test suite for `rates.py` module with 100% coverage
- Error case testing in new `test_money_errors.py` file
- Type hints throughout all modules for better type safety
- Docstrings for all public methods
- `__all__` export declaration in `__init__.py`
- Modern development tool configurations:
  - Black for code formatting (line-length: 99)
  - Ruff for linting with custom rules
  - MyPy for type checking
  - isort for import sorting
- Rate fallback mechanism documentation (searches up to 10 days back)
- Support for Supabase as an additional rate source

### Changed
- Migrated from Poetry to uv for package management
- Replaced all print statements with proper logging calls
- Updated from `os.path` to `pathlib` for file operations
- Converted string formatting to f-strings throughout
- Improved error messages with consistent formatting
- Cache database now uses platform-specific standard locations by default:
  - macOS: `~/Library/Caches/dated_money/exchange-rates.db`
  - Linux: `~/.cache/dated_money/exchange-rates.db`
  - Windows: `%LOCALAPPDATA%\dated_money\cache\exchange-rates.db`
- Fixed bare `except:` clause to catch specific `sqlite3.Error`
- Enhanced precision handling in currency conversion tests
- Modernized Python version support (3.9+)

### Fixed
- Duplicate import statements in `money.py`
- Precision issues in decimal calculations
- Error handling for missing conversion rates
- Thread safety in connection pool implementation

### Removed
- Unnecessary UTF-8 encoding declarations (`# -*- coding: utf-8 -*-`)
- Redundant type imports that are deprecated in modern Python
- Pre-populated exchange rate database from distribution

## Migration Guide from 1.x to 2.0

### Update your imports:
```python
# Old (1.x)
from dmon import Money, Currency

# New (2.0)
from dated_money import Money, Currency
```

### Update your requirements:
```
# Old
dmon>=1.0

# New
dated-money>=2.0
```

### CLI changes:
- The `dmon-rates` command remains the same
- The `dmon` command has been removed (it only printed help text)

## [1.0.2] - Previous Release

### Features
- Basic monetary operations with date-aware currency conversion
- Support for multiple rate sources (local repo, exchangerate-api)
- SQLite caching for exchange rates
- Command-line interface for rate management
