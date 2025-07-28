# Dated Money Examples

This directory contains examples demonstrating the importance of date-aware currency conversion.

## Transaction Analysis Example

The `analyze_transactions.py` script demonstrates why tracking historical exchange rates matters for accurate financial reporting.

### What it does

1. Reads multi-currency transactions from `transactions.csv`
2. Calculates the total value using two methods:
   - **Method 1 (Correct)**: Converts each transaction using the exchange rate from its actual date
   - **Method 2 (Incorrect)**: Converts all transactions using a single date's exchange rates
3. Shows the difference between the two approaches

### Running the example

```bash
# From the project root directory
uv run python examples/analyze_transactions.py
```

### Key insights

The example shows that using current exchange rates for historical transactions can lead to significant errors:
- In our sample data, there's a -0.36% difference
- For larger transaction volumes or more volatile currencies, this difference can be much larger
- The direction of the error depends on how exchange rates have moved over time

### Sample output

The script shows:
- Each transaction converted using its historical rate
- The same transactions converted using a fixed date's rates
- The total difference and percentage error
- How USD/EUR rates changed over the period

This demonstrates why the dated-money library exists: to ensure accurate multi-currency financial calculations that respect the actual transaction dates.