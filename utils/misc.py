"""
Miscellaneous functions
"""
from calendar import isleap
from datetime import date, datetime
import json
import os
from typing import Any, Union

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
