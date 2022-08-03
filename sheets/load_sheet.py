"""
Google Sheets related functions
"""
from typing import Union
import gspread
from gspread.worksheet import Worksheet
from stock import CompanyColumn
from utils import (
    get_env_setting, wrapped_get, COMPANIES_SHEET,
    EFT_SHEET, MUTUAL_SHEET, FUTURES_SHEET, INDEX_SHEET
)
from .spread_ops import (
    client_open_spreadsheet, spreadsheet_worksheets, spreadsheet_add_worksheet
)

DEFAULT_ROWS = 1000
DEFAULT_COLS = 26

# https://docs.gspread.org/

SPREADSHEETS = {}


def open_spreadsheet(name: str) -> gspread.spreadsheet.Spreadsheet:
    """
    Open a spreadsheet

    Args:
        name (str): name of spreadsheet

    Raises:
        ValueError: if spreadsheet not found

    Returns:
        gspread.spreadsheet.Spreadsheet: spreadsheet
    """
    spreadsheet = client_open_spreadsheet(name)
    if spreadsheet:
        SPREADSHEETS[name] = spreadsheet

    return spreadsheet


def init_spreadsheet() -> gspread.spreadsheet.Spreadsheet:
    """
    Initialise app spreadsheet

    Returns:
        gspread.spreadsheet.Spreadsheet: spreadsheet
    """
    name = get_env_setting('SPREADSHEET_NAME', required=True)

    return SPREADSHEETS[name] if name in SPREADSHEETS else \
                open_spreadsheet(name)


def sheet_exists(
        name: str,
        spreadsheet: gspread.spreadsheet.Spreadsheet = None,
        create: bool = False,
        rows: int = DEFAULT_ROWS, cols: int = DEFAULT_COLS
    ) -> Union[gspread.worksheet.Worksheet, None]:
    """
    Check is a worksheet with the specified name exists

    Args:
        name (str): worksheet name
        spreadsheet (gspread.spreadsheet.Spreadsheet): spreadsheet to check;
                                                    default global spreadsheet
        create (bool): create if does not exist; default False
        rows (int, optional): number of rows. Defaults to 1000.
        cols (int, optional): number of columns. Defaults to 26.

    Returns:
        gspread.worksheet.Worksheet: worksheet if exists otherwise None
    """
    if spreadsheet is None:
        spreadsheet = init_spreadsheet()

    the_sheet = None

    if spreadsheet:

        def exists():
            for sheet in spreadsheet_worksheets(spreadsheet):
                if sheet.title == name:
                    worksheet = sheet
                    break
            else:
                worksheet = None

            if not worksheet and create:
                worksheet = add_sheet(name, rows=rows, cols=cols)

            return worksheet

        the_sheet = wrapped_get(exists)

    return the_sheet


def add_sheet(
        name: str, spreadsheet: gspread.spreadsheet.Spreadsheet = None,
        rows: int = DEFAULT_ROWS, cols: int = DEFAULT_COLS
    ) -> gspread.worksheet.Worksheet:
    """
    Add a worksheet with the specified name

    Args:
        name (str): worksheet name
        spreadsheet (gspread.spreadsheet.Spreadsheet, optional):
                spreadsheet to add to. Defaults to application spreadsheet.
        rows (int, optional): number of rows. Defaults to 1000.
        cols (int, optional): number of columns. Defaults to 26.

    Returns:
        gspread.worksheet.Worksheet: worksheet
    """
    if spreadsheet is None:
        spreadsheet = init_spreadsheet()

    worksheet = None
    if spreadsheet:

        def new_sheet():
            return spreadsheet_add_worksheet(spreadsheet, name, rows, cols)

        worksheet = wrapped_get(new_sheet)

    return worksheet


def stock_type_sheet(name: str) -> Worksheet:
    """
    Get a stock type worksheet

    Args:
        name (str): stock type

    Returns:
        Worksheet: worksheet
    """
    return sheet_exists(name, create=True, cols=len(CompanyColumn))


def companies_sheet() -> Worksheet:
    """
    Get the companies worksheet

    Returns:
        Worksheet: companies worksheet
    """
    return stock_type_sheet(COMPANIES_SHEET)


def eft_sheet() -> Worksheet:
    """
    Get the Exchange Traded Fund worksheet

    Returns:
        Worksheet: Exchange Traded Fund worksheet
    """
    return stock_type_sheet(EFT_SHEET)


def mutual_sheet() -> Worksheet:
    """
    Get the Mutual Fund worksheet

    Returns:
        Worksheet: Mutual Fund worksheet
    """
    return stock_type_sheet(MUTUAL_SHEET)


def future_sheet() -> Worksheet:
    """
    Get the Futures worksheet

    Returns:
        Worksheet: Futures worksheet
    """
    return stock_type_sheet(FUTURES_SHEET)


def index_sheet() -> Worksheet:
    """
    Get the Indices worksheet

    Returns:
        Worksheet: Indices worksheet
    """
    return stock_type_sheet(INDEX_SHEET)
