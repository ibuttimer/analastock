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

    @staticmethod
    def stock_param_of(
        symbol: str, from_date: datetime, to_date: datetime) -> object:
        """
        Factory

        Args:
            symbol (str): stock symbol
            from_date (datetime): from date (inclusive)
            to_date (datetime): to date (inclusive)

        Returns:
            StockParam: new object
        """
        stock_param = StockParam(symbol)
        stock_param.from_date = from_date
        stock_param.to_date = to_date
        return stock_param
