"""
Google Sheets related functions
"""
from typing import Union
import os
import gspread
from google.oauth2.service_account import Credentials
from utils import get_env_setting


# https://docs.gspread.org/

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]

CREDENTIALS = Credentials.from_service_account_file(
    os.path.abspath(
        os.path.join(
            get_env_setting('CREDS_PATH', './'),
            get_env_setting('CREDS_FILE', 'creds.json'),
        )
    )
)
SCOPED_CREDENTIALS = CREDENTIALS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDENTIALS)


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
    except gspread.exceptions.SpreadsheetNotFound as exc:
        raise ValueError(f"Spreadsheet {name} not found") from exc

    return spreadsheet


def sheet_exists(
        name: str, spreadsheet: gspread.spreadsheet.Spreadsheet = None
    ) -> Union[gspread.worksheet.Worksheet, None]:
    """
    Check is a worksheet with the specified name exists

    Args:
        name (str): worksheet name
        spreadsheet (gspread.spreadsheet.Spreadsheet): spreadsheet to check;
                                                    default global spreadsheet

    Returns:
        gspread.worksheet.Worksheet: worksheet if exists otherwise None
    """
    if spreadsheet is None:
        spreadsheet = SPREADSHEET

    the_sheet = None

    for sheet in spreadsheet.worksheets():
        if sheet.title == name:
            the_sheet = sheet
            break

    return the_sheet


SPREADSHEET = open_spreadsheet(
                    get_env_setting('SPREADSHEET_NAME', required=True)
                )
