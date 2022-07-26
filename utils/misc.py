"""
Miscellaneous functions
"""
from calendar import isleap
import os
from typing import Any


def get_env_setting(key: str, default_value: Any = None, required: bool = False) -> Any:
    """
    Get an environmental variable

    Args:
        key (str): variable name
        defaultValue (Any, optional): Default value if not present. Defaults to None.
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
        raise ValueError(f"The required setting '{key}' is not specified, please set '{key}'")

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
