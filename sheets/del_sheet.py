"""
Google Sheets related functions
"""
import gspread

from utils import (
    wrapped_get, COMPANIES_SHEET, EFT_SHEET, MUTUAL_SHEET, FUTURES_SHEET,
    INDEX_SHEET, EXCHANGES_SHEET
)
from .load_sheet import init_spreadsheet
from .spread_ops import (
    spreadsheet_worksheets, spreadsheet_del_worksheet
)

# https://docs.gspread.org/


NON_STOCK_SHEETS = [
    EXCHANGES_SHEET, COMPANIES_SHEET, EFT_SHEET, MUTUAL_SHEET, FUTURES_SHEET,
    INDEX_SHEET
]


def del_stock_sheets(
        spreadsheet: gspread.spreadsheet.Spreadsheet = None
) -> None:
    """
    Delete all stock sheets

    Args:
        spreadsheet (gspread.spreadsheet.Spreadsheet): spreadsheet to check;
                                                    default global spreadsheet

    Returns:
        None
    """
    if spreadsheet is None:
        spreadsheet = init_spreadsheet()

    if spreadsheet:

        def delete():
            for sheet in spreadsheet_worksheets(spreadsheet):
                if sheet.title not in NON_STOCK_SHEETS:
                    spreadsheet_del_worksheet(spreadsheet, sheet)

        wrapped_get(delete)
