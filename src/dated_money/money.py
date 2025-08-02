# dated_money.money
# Copyright 2022 Juan Reyero
# SPDX-License-Identifier: MIT

from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from typing import Any, ClassVar, Optional, Union

from dated_money.currency import Currency, CurrencySymbols, to_currency_enum
from dated_money.rates import format_date, get_rates, parse_optional_date

Numeric = Union[int, float, Decimal]

_Cents = "c"


def cents_str(cents: Union[Numeric, str]) -> str:
    return str(cents) + (_Cents if str(cents)[-1] != _Cents else "")


class DatedMoney:
    # Precision for checking equality, applied to the cents.
    # 0 means exact cent matching, higher values allow for more tolerance.
    # For example, precision=2 means 0.01 cent tolerance.
    precision: ClassVar[int] = 0

    def __init__(
        self,
        amount: Union[str, Numeric],
        currency: Union[str, Currency],
        on_date: Optional[Union[date, str]] = None,
    ) -> None:
        """Arguments:

        - amount: It can be a numeric value, or a string. The string
                  can either represent a numeric value, '12.34', or a
                  numeric value plus a 'c' as the last character,
                  '1234c'. In this last case the numeric value is
                  understood to be cents.

        - currency: If a string is provided it should be a
                    three-letter code of a currency in the Currency
                    enum, or a known currency symbol.

        - on_date: If a string is provided it should represent a date
                   in the form yyyy-mm-dd
        """
        self._cents: Decimal = (
            Decimal(amount[:-1])  # '2355c'
            if isinstance(amount, str) and amount[-1] == _Cents
            else (Decimal(amount) * 100)  # '23.55'
        )
        self.currency: Currency = to_currency_enum(currency)
        self.on_date: Optional[date] = parse_optional_date(on_date, defaults_to=None)

    def cents(
        self,
        in_currency: Optional[Union[str, Currency]] = None,
        on_date: Optional[Union[str, date]] = None,
    ) -> Decimal:
        """Converts the money amount to cents.

        Arguments:

        - in_currency: The target currency to convert to. If not
                       provided, the instance's currency is used.
        - on_date: The date in which to convert. If not proviced  the
                   instance's date is used.

        Returns the amount in cents in the specified currency on the
        given date.
        """
        currency = to_currency_enum(in_currency or self.currency)
        if currency == self.currency:
            return self._cents

        rates_date = on_date or self.on_date or date.today()
        rates = get_rates(rates_date, currency, self.currency)

        if rates is None:
            raise RuntimeError(
                f"Could not find exchange rates for {rates_date}. "
                f"Tried local cache, git repo, Supabase, and exchangerate-api.com. "
                f"Check your configuration and network connection."
            )

        if rates[currency] is None:
            raise RuntimeError(
                f"Currency {currency} is not available in the exchange rates for {rates_date}"
            )

        if rates[self.currency] is None:
            raise RuntimeError(
                f"Currency {self.currency} is not available "
                f"in the exchange rates for {rates_date}"
            )

        return self._cents * Decimal(str(rates[currency])) / Decimal(str(rates[self.currency]))

    def amount(
        self, currency: Optional[Union[str, Currency]] = None, rounding: bool = False
    ) -> Decimal:
        cents = self.cents(currency)
        return (Decimal(round(cents)) if rounding else cents) / Decimal("100")

    def to(
        self, currency: Union[str, Currency], on_date: Optional[Union[date, str]] = None
    ) -> "DatedMoney":
        """Returns a new money amount with a different currency.

        Args:
            currency: Target currency as string or Currency enum
            on_date: Optional conversion date.

        Returns:
            New BaseMoney instance in the target currency
        """
        return DatedMoney(
            cents_str(self.cents(currency)),
            currency=currency,
            on_date=parse_optional_date(on_date, defaults_to=self.on_date),
        )

    def on(self, on_date: str) -> "DatedMoney":
        """Create a new money instance with a different date.

        Args:
            on_date: Date string in yyyy-mm-dd format

        Returns:
            New BaseMoney instance with the specified date
        """
        return DatedMoney(cents_str(self._cents), currency=self.currency, on_date=on_date)

    def normalized_amounts(self, other: "DatedMoney") -> tuple[Decimal, Decimal]:
        """Convert both money amounts to the currency of other for operating.

        Args:
            o: Other BaseMoney instance to normalize

        Returns:
            Tuple of (self_cents, other_cents) in the currency of other
        """
        return (self.cents(other.currency), other.cents())

    def __neg__(self) -> "DatedMoney":
        return DatedMoney(cents_str(-self._cents), self.currency, on_date=self.on_date)

    def __add__(self, o: Union["DatedMoney", Numeric, str]) -> "DatedMoney":
        if not isinstance(o, DatedMoney):
            o = DatedMoney(o, self.currency, self.on_date)

        v1, v2 = self.normalized_amounts(o)
        return DatedMoney(cents_str(v1 + v2), o.currency, on_date=o.on_date)

    def __radd__(self, o: Union["DatedMoney", Numeric, str]) -> "DatedMoney":
        return self + o

    def __sub__(self, o: Union["DatedMoney", Numeric, str]) -> "DatedMoney":
        if not isinstance(o, DatedMoney):
            o = DatedMoney(o, self.currency)

        v1, v2 = self.normalized_amounts(o)
        return DatedMoney(cents_str(v1 - v2), o.currency, on_date=o.on_date)

    def __rsub__(self, o: Union["DatedMoney", Numeric, str]) -> "DatedMoney":
        return -self + o

    def __mul__(self, n: Numeric) -> "DatedMoney":
        return DatedMoney(cents_str(self._cents * Decimal(n)), self.currency, on_date=self.on_date)

    __rmul__ = __mul__

    def __truediv__(self, o: Union["DatedMoney", Numeric]) -> Union["DatedMoney", Decimal]:
        if isinstance(o, DatedMoney):
            return self.cents(o.currency) / o.cents()

        return DatedMoney(cents_str(self._cents / Decimal(o)), self.currency, on_date=self.on_date)

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, DatedMoney):
            return NotImplemented
        v1, v2 = self.normalized_amounts(o)
        precision_decimal = Decimal("1").scaleb(-self.precision)
        v1_quantized = v1.quantize(precision_decimal, rounding=ROUND_HALF_UP)
        v2_quantized = v2.quantize(precision_decimal, rounding=ROUND_HALF_UP)
        return v1_quantized == v2_quantized

    def __ne__(self, o: object) -> bool:
        eq_result = self.__eq__(o)
        if eq_result is NotImplemented:
            return NotImplemented
        return not eq_result

    def __gt__(self, o: "DatedMoney") -> bool:
        v1, v2 = self.normalized_amounts(o)
        return v1 > v2

    def __ge__(self, o: "DatedMoney") -> bool:
        eq_result = self.__eq__(o)
        if eq_result is NotImplemented:
            return NotImplemented
        return eq_result or self.__gt__(o)

    def __lt__(self, o: "DatedMoney") -> bool:
        v1, v2 = self.normalized_amounts(o)
        return v1 < v2

    def __le__(self, o: "DatedMoney") -> bool:
        eq_result = self.__eq__(o)
        if eq_result is NotImplemented:
            return NotImplemented
        return eq_result or self.__lt__(o)

    def __str__(self) -> str:
        return f"{CurrencySymbols[self.currency]}{self.amount(self.currency, rounding=True):.2f}"

    def __repr__(self) -> str:
        date_prefix = f"{format_date(self.on_date)} " if self.on_date is not None else ""
        return (
            f"{date_prefix}{self.currency.value.upper()} "
            f"{self.amount(self.currency, rounding=True):.2f}"
        )

    def __conform__(self, protocol: Any) -> Optional[str]:
        """Enables writing to an sqlite database

        https://docs.python.org/3/library/sqlite3.html#how-to-write-adaptable-objects

        Will also need the inverse (string to Money_*) to be registered with
        register_converter.
        """
        import sqlite3

        if protocol is sqlite3.PrepareProtocol:
            return repr(self)
        return None

    @classmethod
    def parse(cls, string: str) -> "DatedMoney":
        components = string.split(" ")
        if len(components) == 3:
            on_date, currency, amount = components
        elif len(components) == 2:
            currency, amount = components
            on_date = None
        else:
            raise ValueError(
                f"Cannot parse money string: '{string}'. "
                f"Expected format: 'YYYY-MM-DD CURRENCY AMOUNT' or 'CURRENCY AMOUNT'"
            )

        return cls(amount, currency, on_date)


def DM(
    base_currency: Union[Currency, str],
    base_date: Optional[Union[date, str]] = None,
):
    """Factory that creates functions that instantiate DatedMoney."""

    def _instantiate(
        amount,
        currency: Optional[Union[Currency, str]] = None,
        on_date: Optional[Union[date, str]] = None,
    ):
        if currency:
            return DatedMoney(amount, currency, on_date=on_date or base_date).to(base_currency)

        return DatedMoney(amount, base_currency, on_date=on_date or base_date)

    return _instantiate


Money = DM
