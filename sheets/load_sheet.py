"""
Google Sheets related functions
"""
from typing import Union
import os
import gspread
from google.oauth2.service_account import Credentials
import google.auth.exceptions
from utils import (
    get_env_setting, error, wrapped_get,
    DEFAULT_GOOGLE_CREDS_FILE, DEFAULT_GOOGLE_CREDS_PATH,
    GOOGLE_CREDS_FILE_ENV, GOOGLE_CREDS_PATH_ENV,
)

DEFAULT_ROWS = 1000
DEFAULT_COLS = 26

# https://docs.gspread.org/

CREDENTIALS = Credentials.from_service_account_file(
    os.path.abspath(
        os.path.join(
            get_env_setting(GOOGLE_CREDS_PATH_ENV, DEFAULT_GOOGLE_CREDS_PATH),
            get_env_setting(GOOGLE_CREDS_FILE_ENV, DEFAULT_GOOGLE_CREDS_FILE),
        )
    )
)
SCOPED_CREDENTIALS = CREDENTIALS.with_scopes([
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
])
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDENTIALS)
SPREADSHEETS = {}

SHEETS_ERR_MSG = 'Google Sheets error, functionality unavailable\n'\
                 'Please check the network connection'


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
    spreadsheet = None
    try:
        spreadsheet = GSPREAD_CLIENT.open(name)
        SPREADSHEETS[name] = spreadsheet
    except gspread.exceptions.SpreadsheetNotFound as exc:
        raise ValueError(f"Spreadsheet {name} not found") from exc
    except google.auth.exceptions.GoogleAuthError:
        error(SHEETS_ERR_MSG)

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
            for sheet in spreadsheet.worksheets():
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
            return spreadsheet.add_worksheet(name, rows, cols)

        worksheet = wrapped_get(new_sheet)

    return worksheet
