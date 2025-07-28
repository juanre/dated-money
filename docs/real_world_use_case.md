# Real-World Use Case: Multi-Currency Sales Tracking

## Your Business Scenario

You have a European company that:
- Has a **base currency** of EUR (for reporting)
- Makes sales in **multiple currencies**
- Has **bank accounts** in some currencies (EUR, USD, GBP)
- Receives payments in currencies where you **don't have accounts** (THB, JPY, etc.)

## The Key Distinction

### Currencies WITH Bank Accounts
When you receive $1000 USD:
- It goes into your USD bank account
- It stays as USD until you decide to convert it
- You want to track it as "$1000 USD received on 2024-01-15"
- Conversion to EUR happens when YOU choose (maybe months later)

### Currencies WITHOUT Bank Accounts  
When you receive ฿5000 THB (Thai Baht):
- You can't hold THB (no account)
- Your payment processor converts it to EUR immediately
- You receive €130 EUR (at that day's rate)
- You want to track: "฿5000 THB received on 2024-01-15 (€130)"

## How Dated Money Helps

```python
from dated_money import Money, Currency
from datetime import date

# Your company's base currency
CompanyMoney = Money(Currency.EUR)

# Track sales throughout the year
sales = []

# January 15: Sale in Thai Baht (no THB account - converted immediately)
sales.append({
    'date': '2024-01-15',
    'description': 'Website sale - Thailand',
    'amount': CompanyMoney(5000, 'THB', on_date='2024-01-15'),
    'converted_immediately': True
})

# January 20: Sale in USD (you have USD account - no immediate conversion)
sales.append({
    'date': '2024-01-20', 
    'description': 'Enterprise license - US',
    'amount': CompanyMoney(1000, 'USD', on_date='2024-01-20'),
    'converted_immediately': False
})

# March 1: Sale in GBP (you have GBP account)
sales.append({
    'date': '2024-03-01',
    'description': 'Consulting - UK',
    'amount': CompanyMoney(800, 'GBP', on_date='2024-03-01'),
    'converted_immediately': False
})

# April 10: Sale in Japanese Yen (no JPY account - converted immediately)
sales.append({
    'date': '2024-04-10',
    'description': 'Software license - Japan',
    'amount': CompanyMoney(50000, 'JPY', on_date='2024-04-10'),
    'converted_immediately': True
})
```

## Viewing Historical Data

### Scenario 1: Year-End Financial Report
You want to see all sales in EUR at their historical conversion rates:

```python
# Each amount uses its original date for conversion
for sale in sales:
    print(f"{sale['date']}: {sale['description']}")
    print(f"  Original: {sale['amount']}")
    print(f"  In EUR: €{sale['amount'].amount():.2f}")
    if sale['converted_immediately']:
        print(f"  (Converted immediately - this is what you actually received)")
    else:
        print(f"  (Still held in {sale['amount'].currency} account)")
    print()
```

Output:
```
2024-01-15: Website sale - Thailand
  Original: THB 5000.00
  In EUR: €130.52
  (Converted immediately - this is what you actually received)

2024-01-20: Enterprise license - US
  Original: $1000.00  
  In EUR: €921.38
  (Still held in Currency.USD account)

2024-03-01: Consulting - UK
  Original: £800.00
  In EUR: €931.20
  (Still held in Currency.GBP account)

2024-04-10: Software license - Japan
  Original: ¥50000.00
  In EUR: €307.45
  (Converted immediately - this is what you actually received)
```

### Scenario 2: Current Portfolio Value
You want to know the current value of money still held in foreign accounts:

```python
# Create a Money class for today's rates
CurrentMoney = Money(Currency.EUR, date.today())

held_funds = [s for s in sales if not s['converted_immediately']]
for sale in held_funds:
    original = sale['amount']
    current = CurrentMoney(original.amount(), original.currency)
    
    print(f"{original.currency} {original.amount()}")
    print(f"  Value on {sale['date']}: €{original.amount(Currency.EUR):.2f}")
    print(f"  Value today: €{current.amount():.2f}")
    print(f"  Difference: €{(current - original).amount():.2f}")
```

## The Power of Dated Money

1. **Historical Accuracy**: The THB and JPY sales show the EUR amount you actually received on those dates

2. **Flexibility**: USD and GBP amounts can be converted using either:
   - Historical rates (for "what was it worth then?")
   - Current rates (for "what is it worth now?")

3. **Audit Trail**: You can always trace back:
   - Original amount and currency
   - Date of transaction
   - Conversion rate used

4. **Natural Operations**: Calculate totals easily:
```python
# Total sales in EUR (using historical rates)
total_sales = sum(sale['amount'] for sale in sales)
print(f"Total sales (historical): €{total_sales.amount():.2f}")

# For held currencies, you might want current values
held_funds = [s['amount'] for s in sales if not s['converted_immediately']]
current_value = sum(CurrentMoney(f.amount(), f.currency) for f in held_funds)
print(f"Current value of held funds: €{current_value.amount():.2f}")
```

## Best Practices for Your Use Case

1. **Use transaction date** for all sales:
   ```python
   sale = CompanyMoney(amount, currency, on_date=transaction_date)
   ```

2. **Track conversion status** separately (as shown above)

3. **For reporting**, distinguish between:
   - Realized conversions (THB, JPY → EUR immediately)
   - Unrealized gains/losses (USD, GBP still held)

4. **For reconciliation**:
   ```python
   # What you actually received in EUR
   realized_eur = sum(s['amount'] for s in sales if s['converted_immediately'])
   
   # What's still in foreign accounts
   unrealized = [s['amount'] for s in sales if not s['converted_immediately']]
   ```

This approach gives you the flexibility to handle both immediate conversions (for currencies without accounts) and deferred conversions (for currencies with accounts) while maintaining accurate historical records.