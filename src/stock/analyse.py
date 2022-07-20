"""
Stock analysis related functions
"""
from datetime import datetime
from typing import List, Tuple, Union
from utils import get_input, error
from .stock_param import StockParam
from .retrieve import download_data, SAMPLE_DATA


DATE_FORM = 'dd-mm-yyyy'
DATE_FORMAT = '%d-%m-%Y'
FRIENDLY_FORMAT = '%d %b %Y'

MIN_DATE = datetime(1962, 2, 1)

SYMBOL_HELP = 'Enter symbol for the stock required.\n'\
              'e.g. IBM: International Business Machines Corporation'
FROM_DATE_HELP = 'Enter analysis start date'
TO_DATE_HELP = 'Enter analysis end date'


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

        if date_time > date_time.now():
            error('Invalid date: future date')
            date_time = None
        if date_time < MIN_DATE:
            error(
                f"Invalid date: shouldn't be prior to "
                f"{MIN_DATE.strftime(FRIENDLY_FORMAT)}"
            )
            date_time = None

    except ValueError:
        error(f'Invalid date: required format is {DATE_FORM}')

    return date_time


def get_stock_param() -> StockParam:
    """
    Get stock parameters

    Returns:
        StockParam: stock parameters
    """
    stock_param = StockParam(
        get_input('Enter stock symbol', help_text=SYMBOL_HELP)
    )

    stock_param.from_date = get_input(
        f'Enter from date [{DATE_FORM}]', validate=validate_date,
        help_text=FROM_DATE_HELP
    )

    def validate_date_after(date_string: str) -> datetime:
        """
        Validate a date string is after the from date

        Args:
            date_string (str): input date string

        Returns:
            Union[datetime, None]: datetime object if valid, otherwise None
        """
        date_time = validate_date(date_string)
        if date_time and date_time < stock_param.from_date:
            date_time = None
            error(
                f'Invalid date: must be after '
                f'{stock_param.from_date.strftime(FRIENDLY_FORMAT)}'
            )

        return date_time

    stock_param.to_date = get_input(
        f'Enter to date [{DATE_FORM}]', validate=validate_date_after,
        help_text=TO_DATE_HELP
    )

    return stock_param


def analyse_stock():
    """ Analyse stock """
    stock_param = get_stock_param()

    download_data(stock_param)


def analyse_ibm():
    """ Analyse IBM stock """
    stock_param = StockParam('ibm')
    stock_param.from_date = datetime(2022, 1, 1)
    stock_param.to_date = datetime(2022, 2, 1)

    download_data(stock_param)


def canned_ibm() -> Tuple[StockParam, List[str]]:
    """ Returned canned IBM stock """
    stock_param = StockParam('ibm')
    stock_param.from_date = datetime(2022, 1, 1)
    stock_param.to_date = datetime(2022, 2, 1)

    return stock_param, SAMPLE_DATA
