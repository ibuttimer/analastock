"""
Stock analysis related functions
"""
from datetime import date, datetime
from typing import List, Union
from copy import copy

import numpy as np
import pandas as pd
from utils import get_input, error
from .data import StockDownload, StockParam
from .enums import DfColumn, DfStat


DATE_FORM = 'dd-mm-yyyy'
DATE_FORMAT = '%d-%m-%Y'
FRIENDLY_FORMAT = '%d %b %Y'

MIN_DATE = datetime(1962, 2, 1)

SYMBOL_HELP = 'Enter symbol for the stock required.\n'\
              'e.g. IBM: International Business Machines Corporation'
FROM_DATE_HELP = 'Enter analysis start date'
TO_DATE_HELP = 'Enter analysis end date'

NUMERIC_COLUMNS = [
    DfColumn.OPEN, DfColumn.HIGH, DfColumn.LOW, DfColumn.CLOSE,
    DfColumn.ADJ_CLOSE, DfColumn.VOLUME
]

PRICE_PRECISION = 6
""" Precision for stock prices """
PERCENT_PRECISION = 2
""" Precision for percentages """


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

        if date_time > datetime.now():
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

    #TODO add 1d, 5d, 3m, 6m, ytd, 1y, 5y options

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


def standardise_stock_param(stock_param: StockParam) -> StockParam:
    """
    Standardise stock parameters by adjusting to be from/to 1st of
    month

    Returns:
        StockParam: a standardised copy of parameters
    """
    std_param = copy(stock_param)   # shallow copy
    if std_param.from_date.day > 1:
        # from 1st of month
        std_param.from_date = std_param.from_date.replace(day=1)

    if std_param.to_date.day > 1:
        year = std_param.to_date.year
        month = std_param.to_date.month + 1
        if month > 12:
            year += 1
            month = 1

        # to 1st of next month
        new_date = std_param.to_date.replace(year=year, month=month, day=1)
        std_param.to_date = min(new_date, datetime.now())

    return std_param


def analyse_stock(
        data_frame: Union[pd.DataFrame, List[str], StockDownload]) -> dict:
    """
    Analyse stock data

    Args:
        data_frame (Union[Pandas.DataFrame, List[str], StockDownload]): data to analyse

    Returns:
        dict: dict of analysis results, like {
            'OpenMin': 11.34,
            'OpenMax': 12.34,
            'OpenChange': 1.0,
            'OpenPercentChange': 8.82,
            .....
        }
    """
    if isinstance(data_frame, StockDownload):
        # take analysis info from data class
        analyse = data_frame.data
        from_date = data_frame.stock_param.from_date
        to_date = data_frame.stock_param.to_date
    else:
        # raw analysis and take date info from data
        analyse = data_frame
        from_date = None
        to_date = None
    if isinstance(analyse, list):
        analyse = data_to_frame(analyse)    # convert list to data frame

    # data in chronological order
    analyse.sort_values(by=DfColumn.DATE.title, ascending=True, inplace=True)
    if not from_date:
        # get date info for raw analysis
        from_date = analyse[DfColumn.DATE.title].min()
        to_date = analyse[DfColumn.DATE.title].max()
    else:
        # filter by min & max dates
        analyse = analyse[(analyse[DfColumn.DATE.title] >= from_date) &
                    (analyse[DfColumn.DATE.title] <= to_date)]

    analysis = {
        'from': from_date if isinstance(from_date, date) else from_date.date(),
        'to': to_date if isinstance(to_date, date) else to_date.date()
    }

    for column in NUMERIC_COLUMNS:
        data_series = analyse[column.title]

        # min value
        analysis[DfStat.MIN.column_key(column)] = data_series.min()

        # max value
        analysis[DfStat.MAX.column_key(column)] = data_series.max()

        # change
        change = round_price(data_series[0] - data_series[len(data_series)-1])
        analysis[DfStat.CHANGE.column_key(column)] = change

        # percentage change
        analysis[DfStat.PERCENT_CHANGE.column_key(column)] = round(
            (change / data_series[0]) * 100, PERCENT_PRECISION
        )

    print(analysis)


def data_to_frame(data: List[str]):
    """
    Convert data to a Pandas DataFrame

    Args:
        data (List[str]): data to convert

    Returns:
        Pandas.DataFrame: data DataFrame
    """
    # split comma-separated string into list of strings
    # https://numpy.org/doc/stable/reference/arrays.ndarray.html
    #
    # Setting arr.dtype is discouraged and may be deprecated in the future.
    # Setting will replace the dtype without modifying the memory
    # https://numpy.org/doc/stable/reference/generated/numpy.ndarray.dtype.html#numpy.ndarray.dtype
    data_records = np.array(
        [entry.split(",") for entry in data]
    )
    # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.from_records.html#pandas.DataFrame.from_records
    data_frame = pd.DataFrame.from_records(data_records, columns=DfColumn.titles())

    # convert numeric columns
    # https://pandas.pydata.org/docs/reference/api/pandas.to_numeric.html
    for column in NUMERIC_COLUMNS:
        data_frame[column.title] = pd.to_numeric(data_frame[column.title])

    # convert date column
    # https://pandas.pydata.org/docs/reference/api/pandas.to_datetime.html#pandas.to_datetime
    data_frame[DfColumn.DATE.title] = pd.to_datetime(
        data_frame[DfColumn.DATE.title].str.lower(), infer_datetime_format=True
    )

    return data_frame


def round_price(price: float) -> float:
    """
    Round a stock price

    Args:
        price (float): stock price

    Returns:
        float: rounded value
    """
    return round(price, PRICE_PRECISION)
