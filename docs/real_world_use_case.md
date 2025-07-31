# Multi-Currency Sales Tracking

A European company (base currency EUR) has bank accounts in EUR and USD. They receive payments in many currencies - some they can hold, others get converted immediately by payment processors.

## Sample Transactions

```python
from dated_money import Money, Currency

# Company reports in EUR
Eur = Money(Currency.EUR)

# Company has a USD account
Usd = Money(Currency.USD)

# Track all 2024 transactions
transactions = [
    # EUR transactions (direct to EUR account)
    {'date': '2024-01-10', 'amount': Eur(500, on_date='2024-01-10'),
     'desc': 'Local client payment'},
    {'date': '2024-06-22', 'amount': Eur(1200, on_date='2024-06-22'),
     'desc': 'EU consulting'},

    # USD transactions (held in USD account)
    {'date': '2024-02-15', 'amount': Usd(1000, on_date='2024-02-15'),
     'desc': 'US software license'},
    {'date': '2024-09-03', 'amount': Usd(2500, on_date='2024-09-03'),
     'desc': 'US enterprise deal'},

    # Other currencies (converted to EUR immediately)
    {'date': '2024-03-20', 'amount': Eur(800, £, on_date='2024-03-20'),
     'desc': 'UK client', 'converted': True},
    {'date': '2024-04-15', 'amount': Eur(50000, 'JPY', on_date='2024-04-15'),
     'desc': 'Japan license', 'converted': True},
    {'date': '2024-07-08', 'amount': Eur(1500, 'CHF', on_date='2024-07-08'),
     'desc': 'Swiss consulting', 'converted': True},
    {'date': '2024-10-25', 'amount': Eur(5000, 'SEK', on_date='2024-10-25'),
     'desc': 'Nordic partnership', 'converted': True},
]
```

## Use Case 1: Year-End Reporting

Show all transactions with their EUR value at the time of receipt:

```python
# Sum all transactions - automatic conversion to EUR using historical rates
total = sum(tx['amount'] for tx in transactions)
print(f"Total revenue: {total}")  # Shows as €X,XXX.XX

# Detailed breakdown
for tx in transactions:
    amount = tx['amount']
    # Original currency display and EUR conversion
    print(f"{tx['date']}: {amount} = {amount.to('EUR')} - {tx['desc']}")
```
```plaintext
Total revenue: €8120.59
2024-01-10: €500.00 = €500.00 - Local client payment
2024-06-22: €1200.00 = €1200.00 - EU consulting
2024-02-15: $1000.00 = €932.60 - US software license
2024-09-03: $2500.00 = €2260.00 - US enterprise deal
2024-03-20: £800.00 = €936.74 - UK client
2024-04-15: JP¥50000.00 = €306.63 - Japan license
2024-07-08: CHF 1500.00 = €1546.89 - Swiss consulting
2024-10-25: kr 5000.00 = €437.73 - Nordic partnership
```

## Use Case 2: With EUR and USD accounts

Assume that you have a USD bank account, and you did not convert the USD sales:

```python
# Filter USD transactions

# Create a Money class for today's rates
Today = Money(Currency.EUR)

usd_amounts = [tx['amount'] for tx in transactions if tx['amount'].currency == Currency.USD]
usd_amounts_today = [amount.on(Today.base_date) for amount in usd_amounts]

print(sum(usd_amounts_today))
# €3012.10

# What if you had converted the sales to EUR as they arrived?
print(sum(usd_amounts))
# €3192.60
```

## Use Case 3: Simulating Conversion Timing

The impact of conversions in different dates:

```python
# Your USD holdings from earlier transactions
usd_balance = sum(usd_amounts)

# Compare conversion values on different dates
conversion_dates = ['2024-06-01', '2024-09-15', '2024-12-01']

print(f"USD Balance: {usd_balance}\n")
print("Conversion simulation:")
for date in conversion_dates:
    eur_value = usd_balance.on(date).to('EUR')
    print(f"  Convert on {date}: {eur_value}")
```
