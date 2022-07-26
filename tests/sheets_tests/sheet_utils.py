"""
Unit tests for sheet find functions
"""
from datetime import date, datetime, timedelta
from typing import Union
import gspread

from utils import last_day_of_month


JAN, FEB, MAR, APR, MAY, JUN, JUL, AUG, SEP, OCT, NOV, DEC = \
    (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)


def add_month(date_time: Union[datetime, date], months: int = 1) -> Union[datetime, date]:
    """
    Add a month to the specified date

    Args:
        date_time (Union[datetime, date]): date
        months (int): number of months to add; default 1

    Returns:
        Union[datetime, date]: new date
    """
    new_date = date_time
    for _ in range(months):
        delta = timedelta(days=last_day_of_month(new_date.year, new_date.month))
        new_date = new_date + delta

    return new_date

def calc_value(month: int, day: int, factor: Union[int, float]) -> Union[int, float]:
    """
    Calculate a test value

    Args:
        month (int): month
        day (int): day
        factor (Union[int, float]): multiplication factor

    Returns:
        Union[int, float]: value
    """
    return (month * factor) + day

def open_value(month: int, day: int) -> float:
    """
    Calculate a test value for Open

    Args:
        month (int): month
        day (int): day

    Returns:
        float: value
    """
    return calc_value(month, day, 5.1)

def high_value(month: int, day: int) -> float:
    """
    Calculate a test value for High

    Args:
        month (int): month
        day (int): day

    Returns:
        float: value
    """
    return calc_value(month, day, 5.2)

def low_value(month: int, day: int) -> float:
    """
    Calculate a test value for Low

    Args:
        month (int): month
        day (int): day

    Returns:
        float: value
    """
    return calc_value(month, day, 5.3)

def close_value(month: int, day: int) -> float:
    """
    Calculate a test value for Close

    Args:
        month (int): month
        day (int): day

    Returns:
        float: value
    """
    return calc_value(month, day, 5.4)

def adj_close_value(month: int, day: int) -> float:
    """
    Calculate a test value for AdjClose

    Args:
        month (int): month
        day (int): day

    Returns:
        float: value
    """
    return calc_value(month, day, 5.5)

def volume_value(month: int, day: int) -> int:
    """
    Calculate a test value for Close

    Args:
        month (int): month
        day (int): day

    Returns:
        float: value
    """
    return calc_value(month, day, 1000)


def add_sheet_data(
        sheet: gspread.worksheet.Worksheet, start_date: date, end_date: date):
    """
    Add generated data to a worksheet

    Args:
        sheet (gspread.worksheet.Worksheet): worksheet to add data to
        start_date (date): start date (day ignored)
        end_date (date): end date (day ignored)
    """
    # TODO don't ignore days, add data from 1st day (inc) to last day (exc)

    data = []
    for year in range(start_date.year, end_date.year + 1):
        if start_date.year == end_date.year:
            # same year
            start_month = start_date.month
            end_month = end_date.month
        else:
            # multiple years
            start_month = 1 if year > start_date.year else start_date.month
            end_month = 12 if year < end_date.year else end_date.month

        for month in range(start_month, end_month + 1):
            data.extend([
                # 31 days in jan/mar, 2022 not a leap year so 28 in feb
                [
                    # columns are 'Date', 'Open', 'High', 'Low', 'Close',
                    # 'AdjClose' & 'Volume', see DfColumn class
                    date(year, month, day).isoformat(),
                    open_value(month, day),
                    high_value(month, day),
                    low_value(month, day),
                    close_value(month, day),
                    adj_close_value(month, day),
                    volume_value(month, day)
                ] for day in range(1, last_day_of_month(year, month) + 1)
            ])

        sheet.append_rows(data, value_input_option='USER_ENTERED')
