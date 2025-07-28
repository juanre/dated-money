#!/usr/bin/env python3
"""
Example: Analyzing Multi-Currency Transactions with Historical Exchange Rates

This example demonstrates why date-aware currency conversion matters by comparing:
1. Converting each transaction using its historical exchange rate
2. Converting all transactions using today's exchange rate

The difference shows the impact of exchange rate fluctuations over time.
"""

import csv
import os
from datetime import date
from decimal import Decimal
from pathlib import Path

# Set up test database for this example
os.environ["DMON_RATES_CACHE"] = str(Path(__file__).parent.parent / "test" / "res")

from dmon import Money, Currency


def read_transactions(csv_file):
    """Read transactions from CSV file."""
    transactions = []
    with open(csv_file, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            transactions.append(
                {
                    "date": row["date"],
                    "amount": Decimal(row["amount"]),
                    "currency": row["currency"],
                    "description": row["description"],
                }
            )
    return transactions


def analyze_transactions():
    """Analyze transactions showing the importance of historical rates."""
    # Your company's base currency is EUR
    CompanyMoney = Money(Currency.EUR)

    # Read transactions
    csv_file = Path(__file__).parent / "transactions.csv"
    transactions = read_transactions(csv_file)

    print("Multi-Currency Transaction Analysis")
    print("=" * 70)
    print()

    # Method 1: Using historical exchange rates (correct approach)
    print("METHOD 1: Using Historical Exchange Rates")
    print("-" * 40)

    historical_total = None
    for tx in transactions:
        # Create money object with the transaction's date
        amount = CompanyMoney(tx["amount"], tx["currency"], on_date=tx["date"])

        # Convert to EUR using the historical rate
        eur_value = amount.to("EUR")

        print(f"{tx['date']}: {amount} = {eur_value} - {tx['description']}")

        # Add to running total
        if historical_total is None:
            historical_total = eur_value
        else:
            historical_total = historical_total + eur_value

    print(f"\nTotal (historical rates): {historical_total}")

    print("\n" + "=" * 70 + "\n")

    # Method 2: Using current exchange rates (incorrect approach)
    print("METHOD 2: Using Current Exchange Rates (INCORRECT)")
    print("-" * 40)

    # For this example, we'll use a date that has complete rate data
    CurrentMoney = Money(Currency.EUR, "2023-10-20")

    current_total = None
    for tx in transactions:
        # Create money object with current date (ignoring transaction date)
        amount = CurrentMoney(tx["amount"], tx["currency"])

        # This uses the exchange rate from 2023-10-20 for all transactions
        eur_value = amount.to("EUR")

        print(
            f"{tx['date']}: {tx['currency']} {tx['amount']} = {eur_value} (using 2023-10-20 rates)"
        )

        # Add to running total
        if current_total is None:
            current_total = eur_value
        else:
            current_total = current_total + eur_value

    print(f"\nTotal (current rates): {current_total}")

    print("\n" + "=" * 70 + "\n")

    # Calculate the difference
    difference = historical_total - current_total
    difference_pct = difference.amount() / historical_total.amount() * 100

    print("SUMMARY")
    print("-" * 40)
    print(f"Total using historical rates: {historical_total}")
    print(f"Total using current rates:    {current_total}")
    print(f"Difference:                   {difference}")
    print(f"Percentage difference:        {difference_pct:.2f}%")
    print()

    # Show exchange rate changes over time for USD
    print("\n" + "=" * 70 + "\n")
    print("USD/EUR Exchange Rate Changes Over Time")
    print("-" * 40)

    for date_str in ["2022-01-07", "2022-07-14", "2023-10-20", "2024-01-15"]:
        usd_100 = CompanyMoney(100, "USD", on_date=date_str)
        eur_value = usd_100.to("EUR")
        print(f"{date_str}: $100 = {eur_value}")


if __name__ == "__main__":
    analyze_transactions()
