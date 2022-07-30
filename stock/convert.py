"""
Stock conversion related functions
"""
from datetime import datetime
from copy import copy

from .data import StockParam


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
        std_param.set_from_date(std_param.from_date.replace(day=1))

    if std_param.to_date.day > 1:
        year = std_param.to_date.year
        month = std_param.to_date.month + 1
        if month > 12:
            year += 1
            month = 1

        # to 1st of next month
        new_date = std_param.to_date.replace(year=year, month=month, day=1)
        std_param.set_to_date(min(new_date, datetime.now()))

    return std_param
