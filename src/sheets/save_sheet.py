"""
Google Sheets related functions
"""
from typing import List
import gspread
import pandas as pd
import numpy as np
from stock import StockParam, DfColumn
from utils import info
from .load_sheet import SPREADSHEET, sheet_exists


# https://docs.gspread.org/


def save_data(stock_param: StockParam, data: List[str]):
    """
    Save data for the specified stock

    Args:
        stock_param (StockParam): stock parameters
        data (List[str]): data to save
    """

    # split comma-separated string into list of strings
    # https://numpy.org/doc/stable/reference/arrays.ndarray.html
    data_records = np.array(
        [entry.split(",") for entry in data]
    )
    # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.from_records.html#pandas.DataFrame.from_records
    df = pd.DataFrame.from_records(data_records, columns=DfColumn.titles())

    sheet = sheet_exists(stock_param.symbol)
    if not sheet:
        sheet = add_sheet(stock_param.symbol)

    values = df.values.tolist()
    sheet.update([df.columns.values.tolist()] + values)

    info(f'Saved {len(values)} records to {stock_param.symbol}')


def add_sheet(name: str) -> gspread.worksheet.Worksheet:
    """
    Add a worksheet with the specified name

    Args:
        name (str): worksheet name

    Returns:
        gspread.worksheet.Worksheet: worksheet
    """
    return SPREADSHEET.add_worksheet(name, 1000, 26)
