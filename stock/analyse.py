"""
Stock analysis related functions
"""
from datetime import date, datetime
from typing import List, Union

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


def validate_symbol(symbol: str) -> Union[str, None]:
    """
    Validate a symbol string

    Args:
        symbol (str): input symbol string

    Returns:
        Union[str, None]: string object if valid, otherwise None
    """
    if symbol.startswith('^'):
        error('Analysis of stock indices is not supported')
        symbol = None

    return symbol


def get_stock_param() -> StockParam:
    """
    Get stock parameters

    Returns:
        StockParam: stock parameters
    """
    #TODO add abort option

    stock_param = StockParam(
        get_input(
            'Enter stock symbol', validate=validate_symbol,
            help_text=SYMBOL_HELP)
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
        analyse = data_frame.data_frame
        from_date = data_frame.stock_param.from_date
        to_date = data_frame.stock_param.to_date
    else:
        # raw analysis and take date info from data
        analyse = data_frame
        from_date = None
        to_date = None
    if isinstance(analyse, list):
        analyse = StockDownload.list_to_frame(analyse)    # convert list to data frame

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

    for column in DfColumn.NUMERIC_COLUMNS:
        data_series = analyse[column.title]

        # min value
        analysis[DfStat.MIN.column_key(column)] = data_series.min()

        # max value
        analysis[DfStat.MAX.column_key(column)] = data_series.max()

        # change
        change = round_price(data_series.iat[0] - data_series.iat[len(data_series)-1])
        analysis[DfStat.CHANGE.column_key(column)] = change

        # percentage change
        analysis[DfStat.PERCENT_CHANGE.column_key(column)] = round(
            (change / data_series.iat[0]) * 100, PERCENT_PRECISION
        )

    print(analysis)


def round_price(price: float) -> float:
    """
    Round a stock price

    Args:
        price (float): stock price

    Returns:
        float: rounded value
    """
    return round(price, PRICE_PRECISION)
