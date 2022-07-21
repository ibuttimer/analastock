"""
Google Sheets related functions
"""
import gspread
import pandas as pd
from stock import StockParam
from stock.enums import DfColumn
from utils import info
from .load_sheet import SPREADSHEET, sheet_exists


# https://docs.gspread.org/


def save_data(stock_param: StockParam, data_frame: pd.DataFrame):
    """
    Save data for the specified stock

    Args:
        stock_param (StockParam): stock parameters
        data_frame (Pandas.DataFrame): data to save
    """
    sheet = sheet_exists(stock_param.symbol)
    if not sheet:
        sheet = add_sheet(stock_param.symbol)

    # data_frame has dates as np.datetime64
    save_frame = pd.DataFrame(data_frame, copy=True)
    save_frame[DfColumn.DATE.title] = save_frame[DfColumn.DATE.title].dt.date

    values = save_frame.to_numpy(dtype=str).tolist()
    sheet.append_rows(values, value_input_option='USER_ENTERED')

    info(f'Saved {len(values)} records to {stock_param.symbol}')


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
