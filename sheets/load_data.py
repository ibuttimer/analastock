"""
Google Sheets data load related functions
"""

from datetime import date
from typing import List, Union
import pandas as pd
from stock import StockParam, DfColumn
from .load_sheet import sheet_exists
from .find_info import read_data_by_date


def get_sheets_data(stock_param: StockParam) -> Union[pd.DataFrame, None]:
    """
    Get data from sheets

    Args:
        stock_param (StockParam): stock parameters

    Returns:
        Union[pd.DataFrame, None]: DataFrame if data found otherwise None
    """
    data = None

    sheet = sheet_exists(stock_param.symbol)
    if sheet:
        data = read_data_by_date(
            sheet,
            stock_param.from_date,
            stock_param.to_date
        )
        if len(data) == 0:
            data = None     # nothing to return

    return data


def check_partial(data_frame: pd.DataFrame, stock_param: StockParam) -> List[StockParam]:
    """
    Check for partial data

    Args:
        data_frame (pd.DataFrame): data to check
        stock_param (StockParam): param for data

    Returns:
        List[StockParam]: list of params representing missing data
    """
    gaps = [] if data_frame is not None else [stock_param]
    gap_param = None

    if data_frame is not None:
        start_year = stock_param.from_date.year
        end_year = stock_param.to_date.year
        for year in range(start_year, end_year + 1):
            if end_year == start_year:
                # same year
                start_month = stock_param.from_date.month
                # stock_param.to_date is excluded
                end_month = stock_param.to_date.month - 1
            else:
                # multiple years
                start_month = 1 if year > start_year else stock_param.from_date.month
                # stock_param.to_date is excluded
                end_month = 12 if year < end_year else stock_param.to_date.month - 1

            for month in range(start_month, end_month + 1):
                check_mth = date(year=year, month=month, day=1)
                limit_mth = date(
                    year=year if month < 12 else year + 1,
                    month=month + 1 if month < 12 else 1,
                    day=1
                )
                mth_frame = data_frame[(data_frame[DfColumn.DATE.title] >= check_mth) &
                            (data_frame[DfColumn.DATE.title] < limit_mth)]
                if len(mth_frame) == 0:
                    # no data for check_mth
                    if not gap_param:
                        # new gap
                        gap_param = StockParam(stock_param.symbol)
                        gap_param.from_date = check_mth
                    gap_param.to_date = limit_mth
                elif gap_param:
                    # save gap
                    gaps.append(gap_param)
                    gap_param = None

        if gap_param:
            # save last gap
            gaps.append(gap_param)

    return gaps
