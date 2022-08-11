"""
Miscellaneous functions
"""
from calendar import isleap
from datetime import date, datetime, time
from typing import Any, Union
from enum import Enum, auto

import pandas as pd

from .constants import FRIENDLY_DATE_FMT


def last_day_of_month(year: int, month: int) -> int:
    """
    Get the last day of the month in the specified year

    Args:
        year (int): year
        month (int): index of month; 1 <= month <= 12

    Returns:
        int: last day
    """
    # 30 days hath sept, apr, jun & nov, all the rest have 31 save
    # feb which one in four has one day more
    return 29 if month == 2 and isleap(year) else \
        28 if month == 2 else \
        30 if month in [9, 4, 6, 11] else 31


def friendly_date(date_time: datetime) -> str:
    """
    Generate a user friendly date string

    Args:
        date_time (datetime): date time

    Returns:
        str: date string
    """
    return date_time.strftime(FRIENDLY_DATE_FMT)


def filter_data_frame_by_date(
        data_frame: pd.DataFrame,
        min_date: Union[datetime, date],
        max_date: Union[datetime, date],
        column: str) -> pd.DataFrame:
    """
    Filter a pandas.DataFrame by dates

    Args:
        data_frame (pd.DataFrame): data frame
        min_date (Union[datetime, date]): min date (inclusive)
        max_date (Union[datetime, date]): max_date (exclusive)
        column (str): column label

    Returns:
        pd.DataFrame: filtered data frame
    """
    if isinstance(min_date, datetime):
        min_date = min_date.date()
    if isinstance(max_date, datetime):
        max_date = max_date.date()

    if isinstance(data_frame[column].iat[0], pd.Timestamp):
        # FutureWarning: Comparison of Timestamp with datetime.date is
        # deprecated
        min_date = pd.Timestamp(min_date)
        max_date = pd.Timestamp(max_date)

    return data_frame[
        (data_frame[column] >= min_date) & (data_frame[column] < max_date)
        ]


class DateFormat(Enum):
    """ Enum representing datetime/date objects conversions """
    DATE = auto()
    """ Convert to date """
    DATETIME = auto()
    """ Convert to datetime """
    FRIENDLY_DATE = auto()
    """ Convert to user friendly string """


def convert_date_time(
        date_time: Union[datetime, date], required: DateFormat
) -> Union[datetime, date, str]:
    """
    Convert datetime/date objects

    Args:
        date_time (Union[datetime, date]): object to convert
        required (DateFormat): required format

    Returns:
        Union[datetime, date, str]: converted object
    """
    conversion = date_time
    if required == DateFormat.DATE:
        if isinstance(date_time, datetime):
            conversion = date_time.date()
    elif required == DateFormat.DATETIME:
        if isinstance(date_time, date):
            conversion = datetime.combine(date_time, time.min)
    elif required == DateFormat.FRIENDLY_DATE:
        conversion = date_time.strftime(FRIENDLY_DATE_FMT)

    return conversion


def drill_dict(source: dict, *args, default_value: Any = None) -> Any:
    """
    Get a values from a dict

    Args:
        source (dict): source dict
        *args (List[str]): path to required value
        default_value (Any, optional): default value. Defaults to None.

    Returns:
        Any: value or ``defaultValue`` if not found
    """
    value = default_value
    obj = source
    for prop in args:
        if prop in obj:
            obj = obj[prop]
        else:
            break
    else:
        value = obj

    return value
