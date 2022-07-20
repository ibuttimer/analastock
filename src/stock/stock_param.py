"""
Stock param related functions
"""
from datetime import datetime
import dataclasses


@dataclasses.dataclass
class StockParam:
    """
    Class representing a stock
    """

    symbol: str
    """ Stock symbol """
    from_date: datetime
    """ From date (inclusive) for data """
    to_date: datetime
    """ To date (inclusive) for data """

    def __init__(self, symbol):
        self.symbol = symbol.upper()

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(' \
               f'{self.symbol}, {self.from_date}, {self.to_date})'
