# Changelog

All notable changes to the dated-money project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
