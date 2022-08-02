"""
Miscellaneous functions
"""
from calendar import isleap
from datetime import date, datetime, time
import json
import os
from typing import Any, Union
from enum import Enum, auto

import pandas as pd

from .constants import FRIENDLY_DATE_FMT
from .output import error


def get_env_setting(
        key: str, default_value: Any = None, required: bool = False) -> Any:
    """
    Get an environmental variable

    Args:
        key (str): variable name
        defaultValue (Any, optional):
                Default value if not present. Defaults to None.
        required (bool): Required flag

    Returns:
        Any: variable value
    """
    value = default_value

    if key in os.environ:
        value = os.environ[key]
        if not value:
            value = default_value

    if not value and required:
        raise ValueError(
            f"The required setting '{key}' is not specified, "\
            f"please set '{key}'")

    return value


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


def load_json_file(filepath: str) -> dict:
    """
    Load json from a file

    Args:
        filepath (str): path to file

    Returns:
        dict: json data
    """
    data = None

    try:
        with open(filepath, encoding='utf-8') as file_handle:
            data = json.load(file_handle)
            file_handle.close()
    except FileNotFoundError:
        error(f'File not found: {filepath}')

    return data


def save_json_file(filepath: str, data: object):
    """
    Save json to a file

    Args:
        filepath (str): path to file
        data (object): json data
    """
    try:
        with open(filepath, mode='w', encoding='utf-8') as file_handle:
            json.dump(data, file_handle, indent=4)
            file_handle.close()
    except OSError:
        error(f'Unable to save file: {filepath}')

    return data


def friendly_date(date_time: datetime) -> str:
    """
    Generate a user friendly date string

    Args:
        date_time (datetime): date time

    Returns:
        str: dat string
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


def drill_dict(source: dict, *args, defaultValue: Any = None) -> Any:
    """
    Get a values from a dict

    Args:
        source (dict): source dict
        *args (List[str]): path to required value
        defaultValue (Any, optional): default value. Defaults to None.

    Returns:
        Any: value or ``defaultValue`` if not found
    """
    value = defaultValue
    obj = source
    for prop in args:
        if prop in obj:
            obj = obj[prop]
        else:
            break
    else:
        value = obj

    return value
