# Understanding Currency Operations in Dated Money

## The Problem It Solves

When dealing with multiple currencies in business, you need to track:
1. The **original amount and currency** 
2. The **date** of the transaction
3. The **exchange rate** used for conversion

This matters because €100 received in January might have been $110, but €100 received in July might have been $105.

## Core Concepts

### Money = Amount + Currency + Date

```python
# Create a payment received on a specific date
payment = CompanyMoney(1000, 'USD', on_date='2024-01-15')
```

This tracks:
- Amount: $1000
- Currency: USD  
- Date: January 15, 2024
- Conversion rate: Whatever USD/EUR was on that date

### Addition Preserves History

When you add money from different dates or currencies:

```python
jan_payment = CompanyMoney(1000, 'USD', on_date='2024-01-15')  # $1000
feb_payment = CompanyMoney(2000, 'USD', on_date='2024-02-15')  # $2000

total = jan_payment + feb_payment  # €2,847 (using January's rate)
```

The result uses the **first operand's date** for consistency.

### Different Currencies Convert Automatically

```python
usd_payment = CompanyMoney(1000, 'USD', on_date='2024-01-15')
gbp_payment = CompanyMoney(500, 'GBP', on_date='2024-01-15')
thb_payment = CompanyMoney(5000, 'THB', on_date='2024-01-15')

# Total in EUR (your base currency)
total = usd_payment + gbp_payment + thb_payment
print(f"Total: €{total.amount():.2f}")
```

## Why Dates Matter: A Practical Example

Consider a business that receives payments throughout the year:

```python
CompanyMoney = Money(Currency.EUR)

# Q1 sale when EUR was strong
q1_sale = CompanyMoney(10000, 'USD', on_date='2024-01-15')
print(f"Q1: $10,000 = €{q1_sale.amount():.2f}")  # €9,213.80

# Q3 sale when EUR weakened  
q3_sale = CompanyMoney(10000, 'USD', on_date='2024-07-15')
print(f"Q3: $10,000 = €{q3_sale.amount():.2f}")  # €9,524.60

# Same USD amount, different EUR value due to exchange rate changes
difference = q3_sale.amount() - q1_sale.amount()
print(f"Exchange rate impact: €{difference:.2f}")
```

## Key Benefits

1. **Historical Accuracy**: Financial reports show the actual value at the time of transaction
2. **Audit Trail**: You can always trace back to original amounts and rates
3. **Flexibility**: Convert to any currency using the appropriate historical rate
4. **Simplicity**: Just add amounts together - the library handles the complexity

## Common Use Cases

### Multi-Currency Sales Tracking
```python
sales = [
    CompanyMoney(5000, 'THB', on_date='2024-01-15'),   # Thai customer
    CompanyMoney(1000, 'USD', on_date='2024-01-20'),   # US customer
    CompanyMoney(800, 'GBP', on_date='2024-02-01'),    # UK customer
]

total_revenue = sum(sales)
print(f"Total revenue: €{total_revenue.amount():.2f}")
```

### Currency Conversion Timing
```python
# Money received in January
jan_usd = CompanyMoney(10000, 'USD', on_date='2024-01-15')

# If you convert it today vs. when received
CurrentMoney = Money(Currency.EUR, date.today())
current_value = CurrentMoney(10000, 'USD')

print(f"Value when received: €{jan_usd.amount():.2f}")
print(f"Value if converted today: €{current_value.amount():.2f}")
```

This is crucial for understanding realized vs. unrealized currency gains/losses.