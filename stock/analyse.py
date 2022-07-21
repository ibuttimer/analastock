"""
Stock analysis related functions
"""
from datetime import datetime
from typing import List, Tuple, Union

import numpy as np
import pandas as pd
from utils import get_input, error
from .stock_param import StockParam
from .retrieve import download_data, SAMPLE_DATA
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

    # TODO add 1d, 5d, 3m, 6m, ytd, 1y, 5y options

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


def analyse_stock(data_frame: pd.DataFrame) -> dict:
    """
    Analyse stock data

    Args:
        data_frame (Pandas.DataFrame): data to analyse

    Returns:
        dict: dict of analysis results, like {
            'OpenMin': 11.34,
            'OpenMax': 12.34,
            'OpenChange': 1.0,
            'OpenPercentChange': 8.82,
            .....
        }
    """
    analysis = {}

    for column in NUMERIC_COLUMNS:
        data_series = data_frame[column.title]

        # min value
        analysis[DfStat.MIN.column_key(column)] = data_series.min()

        # max value
        analysis[DfStat.MAX.column_key(column)] = data_series.max()

        # change
        change = round(
            data_series[0] - data_series[len(data_series)-1], PRICE_PRECISION
        )
        analysis[DfStat.CHANGE.column_key(column)] = change

        # percentage change
        analysis[DfStat.PERCENT_CHANGE.column_key(column)] = round(
            (change / data_series[0]) * 100, PERCENT_PRECISION
        )

    print(analysis)


def analyse_ibm():
    """ Analyse IBM stock """
    stock_param = StockParam('ibm')
    stock_param.from_date = datetime(2022, 1, 1)
    stock_param.to_date = datetime(2022, 2, 1)

    data_frame = data_to_frame(SAMPLE_DATA)

    analyse_stock(data_frame)


def canned_ibm() -> Tuple[StockParam, pd.DataFrame]:
    """ Returned canned IBM stock """
    stock_param = StockParam('ibm')
    stock_param.from_date = datetime(2022, 1, 1)
    stock_param.to_date = datetime(2022, 2, 1)

    return stock_param, data_to_frame(SAMPLE_DATA)


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
