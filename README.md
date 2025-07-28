# Dated Money

Dated Money is a Python library for manipulating monetary values with control over the date on which currency conversions take place. It represents each monetary value as an amount (stored as a Decimal in cents) and a currency, along with a corresponding date.

## Why This Library Exists

If you're handling multi-currency transactions, you need to know not just "how much" but also "when" - because exchange rates change daily. This is critical for:

- **Businesses receiving payments in multiple currencies**: Track the exact value received on the date of transaction
- **Accurate financial reporting**: Use historical exchange rates for past transactions
- **Multi-currency portfolios**: Keep amounts in their original currency until you decide to convert

For example, if you receive ฿5000 (Thai Baht) on January 15th and it's immediately converted to €130, you need to record both the original amount AND the historical rate used. That's what Dated Money does.

## Key Features

- **Date-aware currency conversion**: Perform accurate conversions based on historical exchange rates
- **Multiple rate sources**: Supports local repositories, Supabase, and exchangerate-api.com
- **Automatic rate fallback**: If rates aren't available for a specific date, automatically searches up to 10 days back
- **Type-safe**: Comprehensive type hints throughout the codebase
- **Well-tested**: Extensive test suite with error case coverage
- **Modern Python**: Uses pathlib, f-strings, and proper logging


## Features

- Perform arithmetic operations on monetary values with different currencies and dates
- Convert monetary values between currencies based on exchange rates for specific dates
- Fetch and cache exchange rates from external APIs or local repositories
- Flexible configuration through environment variables

## Installation

You can install Dated Money using uv (recommended):

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
git clone https://github.com/juanre/dmon
cd dmon
uv sync
```

## Usage

### Real-World Example

Imagine you run a European company receiving payments in multiple currencies:

```python
from dmon import Money, Currency

# Your company's base currency
CompanyMoney = Money(Currency.EUR)

# Payment received in Thai Baht (immediately converted to EUR)
thb_payment = CompanyMoney(5000, 'THB', on_date='2024-01-15')
print(f"Received {thb_payment} = €{thb_payment.amount():.2f}")
# Output: Received THB 5000.00 = €130.52

# Payment received in USD (kept in USD account)
usd_payment = CompanyMoney(1000, 'USD', on_date='2024-01-15')  
print(f"Received {usd_payment} = €{usd_payment.amount():.2f} at historical rate")
# Output: Received USD 1000.00 = €921.38 at historical rate

# Calculate total revenue in EUR
total = thb_payment + usd_payment
print(f"Total revenue: €{total.amount():.2f}")
# Output: Total revenue: €1051.90
```

### Basic Examples

```python
from decimal import Decimal as Dec
from dmon import Money, Currency

# Create a Money class with EUR as the base currency and conversion rates from a specific date
date_a = '2022-07-14'
Eur = Money(Currency.EUR, date_a)

# Create a Money class with AUD as the base currency and conversion rates from the same date
Aud = Money(base_currency='A$', base_date=date_a)

# Create monetary values in different currencies
price_eur = Eur(100)  # €100
price_usd = Eur(120, Currency.USD)  # $120
price_gbp = Eur(80, '£')  # £80

# Values are stored in cents and can be accessed in any currency
assert Eur(23, '€').cents('eur') == 2300
assert Eur(40).cents('usd') == Dec('4020.100502512562832012897042')

# Values can be created in any currency, regardless of the base currency
assert Eur(20, '£') == Aud(20, '£')

# Perform arithmetic operations
total = price_eur + price_usd + price_gbp
assert str(total) == '€270.40'  # Total in the base currency (EUR)

# Convert to a specific currency
total_usd = total.to(Currency.USD)
assert str(total_usd) == '$303.89'

# Compare monetary values
assert price_eur < price_usd
assert price_gbp == Eur(80, Currency.GBP)
```

### Operations with Different Currencies and Dates

You can perform operations on monetary values with different currencies and conversion dates:

```python
date_a = '2022-07-14'
date_b = '2022-01-07'

Eur = Money(Currency.EUR, date_a)
OldEur = Money('€', date_b)
Aud = Money(Currency.AUD, date_a)

# Operations between instances with different dates return an instance with the base date of the first element
adds = OldEur(10) + Eur(30)
assert adds.amount() == 40
assert adds.on_date == OldEur.base_date

# Operations between instances with different currencies return a result in the base currency
result = Eur(10, '$') + Eur(20, 'CAD')
assert result.currency == Currency.EUR

# Changing the reference dates affects the operation results
assert Eur(10, '$', date_a) + Eur(20, 'CAD', date_a) != Eur(10, '$', date_b) + Eur(20, 'CAD', date_b)

# Perform various arithmetic operations
assert Aud(10) + Eur(20) == Aud(39.70) == Eur(39.7, 'aud')
assert Eur(20) + Aud(10) == Eur(26.73)
assert (Aud(10) + Eur(20)).currency == Currency.AUD
assert (Eur(20) + Aud(10)).currency == Currency.EUR
assert Eur(20, 'aud') + Eur(20, 'gbp') == Aud(20, 'aud') + Aud(20, 'gbp')
```

### Using a Single Money Class

In normal use, you will probably create a single Money class with your preferred base currency and use it to handle monetary values in various currencies:

```python
Eur = Money(Currency.EUR)

price_eur = Eur(100)  # €100
price_usd = Eur(120, Currency.USD)  # $120
price_gbp = Eur(80, '£')  # £80

total = price_eur + price_usd + price_gbp
assert str(total) == '€304.71'  # Total in the base currency (EUR)

assert price_usd.currency == Currency.USD
assert price_gbp.currency == Currency.GBP
```

### Configuring Exchange Rates

Dated Money supports multiple sources for exchange rates, checked in this order:

1. **Local SQLite cache** (fastest)
2. **Local git repository** (for offline use)
3. **Supabase** (for shared team rates)
4. **exchangerate-api.com** (for fresh rates)

#### Rate Fallback Behavior

If exchange rates are not available for the requested date, Dated Money automatically searches for rates from previous dates, going back up to 10 days. This ensures that currency conversions work even on weekends or holidays when fresh rates might not be available. When fallback rates are used, a log message indicates which date's rates were actually used.

#### Environment Variables

- `DMON_RATES_CACHE`: Directory for the SQLite cache database (default: current directory)

- `DMON_RATES_REPO`: Directory containing a git repository with exchange rates in a `money` subdirectory

- `SUPABASE_URL` and `SUPABASE_KEY`: Credentials for Supabase integration

- `DMON_EXCHANGERATE_API_KEY`: API key for exchangerate-api.com (required for historical rates on paid plans)

#### Rate File Format

Rate files should be named `yyyy-mm-dd-rates.json` and contain:


```
    {
     "conversion_rates":{
      "USD":1,
      "AED":3.6725,
      "AFN":71.3141,
    ...}
    }
```

### Creating the Cache Database

To create the cache database, follow these steps:

1. Set the `DMON_RATES_CACHE` environment variable:
   ```
   export DMON_RATES_CACHE=~/.dmon
   ```

2. Create the database cache table:
   ```
   dmon-rates --create-table
   ```

If you have a paid API key for https://exchangerate-api.com, you can set the `DMON_EXCHANGERATE_API_KEY` environment variable and create your cache with:

```
dmon-rates --fetch-rates 2021-10-10:2021-10-20
```

## Development

This project uses modern Python development tools:

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

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request on the [GitHub repository](https://github.com/juanre/dmon).

## License

Dated Money is released under the [MIT License](https://opensource.org/licenses/MIT).
