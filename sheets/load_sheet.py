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

try:
    SPREADSHEET = GSPREAD_CLIENT.open(
        get_env_setting('SPREADSHEET_NAME', required=True)
    )
except gspread.exceptions.SpreadsheetNotFound as exc:
    spreadsheet = get_env_setting('SPREADSHEET_NAME')
    raise ValueError(f"Spreadsheet {spreadsheet} not found") from exc


def load_sheet():

    worksheets = SPREADSHEET.worksheets()
    print(SPREADSHEET.worksheets())


    print(sheet_exists(worksheets[0].title))


def sheet_exists(name: str) -> Union[gspread.worksheet.Worksheet, None]:
    """
    Check is a worksheet with the specified name exists

    Args:
        name (str): worksheet name

    Returns:
        gspread.worksheet.Worksheet: worksheet if exists otherwise None
    """
    the_sheet = None

    for sheet in SPREADSHEET.worksheets():
        if sheet.title == name:
            the_sheet = sheet
            break

    return the_sheet
