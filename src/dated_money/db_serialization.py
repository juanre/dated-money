# dated_money.db_serialization
# Copyright 2022 Juan Reyero
# SPDX-License-Identifier: MIT

"""Database serialization support for DatedMoney objects.

This module provides utilities for storing and retrieving DatedMoney objects
in SQLite and PostgreSQL databases.
"""

import sqlite3
from typing import Union

from dated_money.money import DatedMoney


def register_sqlite_converters():
    """Register SQLite converters for DatedMoney serialization.

    This enables automatic conversion of DatedMoney objects when storing
    and retrieving from SQLite databases.

    Example:
        >>> import sqlite3
        >>> from dated_money import DatedMoney
        >>> from dated_money.db_serialization import register_sqlite_converters
        >>>
        >>> # Register converters
        >>> register_sqlite_converters()
        >>>
        >>> # Create connection with type detection
        >>> conn = sqlite3.connect(':memory:', detect_types=sqlite3.PARSE_DECLTYPES)
        >>> cursor = conn.cursor()
        >>>
        >>> # Create table with DATEDMONEY type
        >>> cursor.execute('''
        ...     CREATE TABLE transactions (
        ...         id INTEGER PRIMARY KEY,
        ...         amount DATEDMONEY
        ...     )
        ... ''')  # doctest: +ELLIPSIS
        <sqlite3.Cursor object at 0x...>
        >>>
        >>> # Store and retrieve DatedMoney objects
        >>> money = DatedMoney(100, 'EUR', '2024-01-01')
        >>> cursor.execute("INSERT INTO transactions (amount) VALUES (?)", (money,))  # doctest: +ELLIPSIS
        <sqlite3.Cursor object at 0x...>
        >>> cursor.execute("SELECT amount FROM transactions")  # doctest: +ELLIPSIS
        <sqlite3.Cursor object at 0x...>
        >>> retrieved = cursor.fetchone()[0]
        >>> assert isinstance(retrieved, DatedMoney)
    """

    def convert_datedmoney(value: bytes) -> DatedMoney:
        """Convert stored string back to DatedMoney."""
        try:
            return DatedMoney.parse(value.decode("utf-8"))
        except (ValueError, Exception) as e:
            # Re-raise as ValueError for consistency
            raise ValueError(
                f"Cannot parse DatedMoney from database: {value.decode('utf-8')}"
            ) from e

    sqlite3.register_converter("DATEDMONEY", convert_datedmoney)


# PostgreSQL type casting functions
def to_postgres(money: DatedMoney) -> str:
    """Convert DatedMoney to PostgreSQL-compatible string.

    Args:
        money: DatedMoney instance to convert

    Returns:
        String representation suitable for PostgreSQL storage
    """
    return repr(money)


def from_postgres(value: Union[str, None]) -> Union[DatedMoney, None]:
    """Convert PostgreSQL string to DatedMoney.

    Args:
        value: String value from PostgreSQL

    Returns:
        DatedMoney instance or None if value is None
    """
    if value is None:
        return None
    return DatedMoney.parse(value)


# Example PostgreSQL usage with psycopg2
POSTGRES_EXAMPLE = """
# Example: Using DatedMoney with PostgreSQL and psycopg2

import psycopg2
from dated_money import DatedMoney
from dated_money.db_serialization import to_postgres, from_postgres

# Create table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id SERIAL PRIMARY KEY,
        amount TEXT,  -- Store as TEXT
        description TEXT
    )
''')

# Insert DatedMoney
money = DatedMoney(100.50, 'EUR', '2024-01-01')
cursor.execute(
    "INSERT INTO transactions (amount, description) VALUES (%s, %s)",
    (to_postgres(money), "Test transaction")
)

# Retrieve and convert back
cursor.execute("SELECT amount FROM transactions WHERE id = %s", (1,))
row = cursor.fetchone()
money_retrieved = from_postgres(row[0])
"""
