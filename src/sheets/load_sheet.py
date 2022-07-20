"""
Google Sheets related functions
"""
from typing import Union
import os
import gspread
from google.oauth2.service_account import Credentials


# https://docs.gspread.org/

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]

CREDENTIALS = Credentials.from_service_account_file(
    os.path.abspath(
        os.path.join(
            os.environ['CREDS_PATH']
                if os.environ['CREDS_PATH'] else './',
            os.environ['CREDS_FILE']
                if os.environ['CREDS_FILE'] else 'creds.json'
        )
    )
)
SCOPED_CREDENTIALS = CREDENTIALS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDENTIALS)

if not os.environ['SPREADSHEET_NAME']:
    raise ValueError('Spreadsheet name not specified, set SPREADSHEET_NAME')

SPREADSHEET = GSPREAD_CLIENT.open(os.environ['SPREADSHEET_NAME'])


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
