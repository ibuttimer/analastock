"""
Google Sheets related functions
"""
from typing import Union
import gspread
import pandas as pd
from stock import StockParam, DfColumn, StockDownload
from utils import info
from .load_sheet import SPREADSHEET, sheet_exists


# https://docs.gspread.org/


def save_data(data: Union[pd.DataFrame, StockDownload], stock_param: StockParam = None):
    """
    Save data for the specified stock

    Args:
        data_frame (Union[pandas.DataFrame, StockDownload]): data to save
        stock_param (StockParam): stock parameters if data is DataFrame, ignored otherwise
    """
    if isinstance(data, StockDownload):
        data_frame = data.data_frame
        symbol = data.stock_param.symbol
    else:
        data_frame = data
        symbol = stock_param.symbol

    sheet = sheet_exists(symbol)
    if not sheet:
        sheet = add_sheet(symbol)

    # data_frame has dates as np.datetime64
    save_frame = pd.DataFrame(data_frame, copy=True)
    # convert to datetime.date objects
    # https://pandas.pydata.org/docs/reference/api/pandas.Series.dt.date.html#pandas.Series.dt.date
    save_frame[DfColumn.DATE.title] = save_frame[DfColumn.DATE.title].dt.date

    values = save_frame.to_numpy(dtype=str).tolist()
    sheet.append_rows(values, value_input_option='USER_ENTERED')

    info(f'Saved {len(values)} records to {symbol}')


def add_sheet(
        name: str, spreadsheet: gspread.spreadsheet.Spreadsheet = None
    ) -> gspread.worksheet.Worksheet:
    """
    Add a worksheet with the specified name

    Args:
        name (str): worksheet name
        spreadsheet (gspread.spreadsheet.Spreadsheet): spreadsheet to add to;
                                                    default global spreadsheet

    Returns:
        gspread.worksheet.Worksheet: worksheet
    """
    if spreadsheet is None:
        spreadsheet = SPREADSHEET
    return spreadsheet.add_worksheet(name, 1000, 26)
