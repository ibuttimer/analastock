"""
Stock analysis related functions
"""
from datetime import datetime
from typing import Union
from utils import get_input, error
from .stock_param import StockParam
from .retrieve import download_data


DATE_FORM = 'dd-mm-yyyy'
DATE_FORMAT = '%d-%m-%Y'


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
    stock_param = StockParam(
        get_input('Enter stock symbol')
    )

    stock_param.from_date = get_input(
        f'Enter from date [{DATE_FORM}]', validate=validate_date)

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
            error(f'Invalid date: must be after {stock_param.from_date.strftime(DATE_FORMAT)}')

        return date_time

    stock_param.to_date = get_input(
        f'Enter to date [{DATE_FORM}]', validate=validate_date_after)

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
