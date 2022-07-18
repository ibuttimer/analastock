"""
Stock analysis related functions
"""
from datetime import datetime
from typing import Union
from utils import get_input, error


DATE_FORM = 'dd-mm-yyyy'
DATE_FORMAT = '%d-%m-%Y'


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
        self.symbol = symbol

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(' \
               f'{self.symbol}, {self.from_date}, {self.to_date})'


def validate_date(date_string: str) -> Union[datetime, None]:
    """
    Validate a date string

    Args:
        date_string (str): input date string

    Returns:
        Union[datetime, None]: datetime object if valid, otherwise None
    """
    date_time = None
    try:
        date_time = datetime.strptime(date_string, DATE_FORMAT)
    except ValueError:
        error(f'Invalid date: required format is {DATE_FORM}')

    return date_time


def get_stock_param() -> StockParam:
    """
    Get stock parameters

    Returns:
        StockParam: stock parameters
    """
    stock = StockParam(
        get_input('Enter stock symbol')
    )

    stock.from_date = get_input(
        f'Enter from date [{DATE_FORM}]', validate=validate_date)

    def validate_date_after(date_string: str) -> datetime:

        date_time = validate_date(date_string)
        if date_time and date_time < stock.from_date:
            date_time = None
            error(f'Invalid date: must be after {stock.from_date.strftime(DATE_FORMAT)}')

        return date_time


    stock.to_date = get_input(
        f'Enter to date [{DATE_FORM}]', validate=validate_date_after)


    return stock


def analyse_stock():
    """_Analyse stock """
    stock_param = get_stock_param()
