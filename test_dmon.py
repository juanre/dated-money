# from dated_money import Money, Currency
#
# # Company reports in EUR
# Eur = Money(Currency.EUR)
# Usd = Money(Currency.USD)
#
# # Demonstration
# print("\nChecking base_currency of Money factories:")
# print(f"Eur.base_currency: {Eur.base_currency}")
# print(f"Usd.base_currency: {Usd.base_currency}")
#
# print("\nDemonstration of sum():")
# usd1 = Usd(1000, on_date='2024-02-15')
# usd2 = Usd(2500, on_date='2024-09-03')
# print(f"usd1: {usd1} (currency: {usd1.currency})")
# print(f"usd2: {usd2} (currency: {usd2.currency})")
#
# # Check if originals are modified
# print("\nBefore sum:")
# print(f"usd1._cents: {usd1._cents}")
# print(f"usd2._cents: {usd2._cents}")
#
# result = usd1 + usd2
# print(f"\nAfter sum: {result} (currency: {result.currency})")
# print(f"usd1._cents: {usd1._cents} (unchanged)")
# print(f"usd2._cents: {usd2._cents} (unchanged)")
# print("---")
#
# # Track all 2024 transactions
# transactions = [
#     # EUR transactions (direct to EUR account)
#     {'date': '2024-01-10', 'amount': Eur(500, on_date='2024-01-10'),
#      'desc': 'Local client payment'},
#     {'date': '2024-06-22', 'amount': Eur(1200, on_date='2024-06-22'),
#      'desc': 'EU consulting'},
#
#     # USD transactions (held in USD account)
#     {'date': '2024-02-15', 'amount': Usd(1000, on_date='2024-02-15'),
#      'desc': 'US software license'},
#     {'date': '2024-09-03', 'amount': Usd(2500, on_date='2024-09-03'),
#      'desc': 'US enterprise deal'},
#
#     # Other currencies (converted to EUR immediately)
#     {'date': '2024-03-20', 'amount': Eur(800, 'GBP', on_date='2024-03-20'),
#      'desc': 'UK client', 'converted': True},
#     {'date': '2024-04-15', 'amount': Eur(50000, 'JPY', on_date='2024-04-15'),
#      'desc': 'Japan license', 'converted': True},
#     {'date': '2024-07-08', 'amount': Eur(1500, 'CHF', on_date='2024-07-08'),
#      'desc': 'Swiss consulting', 'converted': True},
#     {'date': '2024-10-25', 'amount': Eur(5000, 'SEK', on_date='2024-10-25'),
#      'desc': 'Nordic partnership', 'converted': True},
# ]
#
# Today = Money(Currency.EUR)
#
# usd_amounts = [tx['amount'] for tx in transactions if tx['amount'].currency == Currency.USD]
# usd_amounts_today = [amount.on(Today.base_date) for amount in usd_amounts]
#
# total_usd = sum(usd_amounts_today)
# print(total_usd)
# # €3012.10
#
# # What if you had converted the sales to EUR as they arrived?
# print(sum(usd_amounts))
# # €3192.60
#
# # Your USD holdings from earlier transactions
# print("\nChecking individual USD amounts:")
# for amt in usd_amounts:
#     print(f"  {amt} (currency: {amt.currency})")
#
# usd_balance = sum(usd_amounts)
# print(f"\nSum result: {usd_balance} (currency: {usd_balance.currency})")
#
# # Compare conversion values on different dates
# conversion_dates = ['2024-06-01', '2024-09-15', '2024-12-01']
#
# print(f"\nUSD Balance: {usd_balance}\n")
# print("Conversion simulation:")
# for date in conversion_dates:
#     eur_value = usd_balance.on(date).to('EUR')
#     print(f"  Convert on {date}: {eur_value}")
#
#
# # Your USD holdings from earlier transactions
# usd_balance = sum(usd_amounts)
#
# # Compare conversion values on different dates
# conversion_dates = ['2024-06-01', '2024-09-15', '2024-12-01']
#
# print(f"USD Balance: {usd_balance}\n")
# print("Conversion simulation:")
# for date in conversion_dates:
#     eur_value = usd_balance.on(date).to('EUR')
#     print(f"  Convert on {date}: {eur_value}")
#
# print('-----------------------')
from dated_money import Money, Currency

# Company reports in EUR
Eur = Money(Currency.EUR)

# Company has a USD account
Usd = Money(Currency.USD)

# Track all 2024 transactions
transactions = [
    # EUR transactions (direct to EUR account)
    {
        "date": "2024-01-10",
        "amount": Eur(500, on_date="2024-01-10"),
        "desc": "Local client payment",
    },
    {"date": "2024-06-22", "amount": Eur(1200, on_date="2024-06-22"), "desc": "EU consulting"},
    # USD transactions (held in USD account)
    {
        "date": "2024-02-15",
        "amount": Usd(1000, on_date="2024-02-15"),
        "desc": "US software license",
    },
    {
        "date": "2024-09-03",
        "amount": Usd(2500, on_date="2024-09-03"),
        "desc": "US enterprise deal",
    },
    # Other currencies
    {
        "date": "2024-03-20",
        "amount": Eur(800, "£", on_date="2024-03-20"),
        "desc": "UK client",
        "converted": True,
    },
    {
        "date": "2024-04-15",
        "amount": Eur(50000, "JPY", on_date="2024-04-15"),
        "desc": "Japan license",
        "converted": True,
    },
    {
        "date": "2024-07-08",
        "amount": Eur(1500, "CHF", on_date="2024-07-08"),
        "desc": "Swiss consulting",
        "converted": True,
    },
    {
        "date": "2024-10-25",
        "amount": Eur(5000, "SEK", on_date="2024-10-25"),
        "desc": "Nordic partnership",
        "converted": True,
    },
]

# Sum all transactions - automatic conversion to EUR using historical rates
total = sum(tx["amount"] for tx in transactions)
print(f"Total revenue: {total}")  # Shows as €X,XXX.XX

# Detailed breakdown
for tx in transactions:
    amount = tx["amount"]
    # Original currency display and EUR conversion
    print(f"{tx['date']}: {amount} = {amount.to('EUR')} - {tx['desc']}")

# Filter USD transactions

# Create a Money class for today's rates
Today = Money(Currency.EUR)

usd_amounts = [tx["amount"] for tx in transactions if tx["amount"].currency == Currency.USD]
usd_amounts_today = [amount.on(Today.base_date) for amount in usd_amounts]

print(sum(usd_amounts_today).to("€"))
# €3053.40

print([a.to("€") for a in usd_amounts])
# [2024-02-15 EUR 932.60, 2024-09-03 EUR 2260.00]

total = usd_amounts[0].to("€")
print(total)
for a in usd_amounts[1:]:
    total += a.to("€")
print()
print(total)

print(sum([a.to("€") for a in usd_amounts]))
# €3192.60

# # Your USD holdings from earlier transactions
# usd_balance = sum(usd_amounts)
#
# # Compare conversion values on different dates
# conversion_dates = ['2024-06-01', '2024-09-15', '2024-12-01']
#
# print(f"USD Balance: {usd_balance}\n")
# print("Conversion simulation:")
# for date in conversion_dates:
#     eur_value = usd_balance.on(date).to('EUR')
#     print(f"  Convert on {date}: {eur_value}")
