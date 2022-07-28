"""
Google Sheets related functions
"""
from typing import Union
import os
import gspread
from google.oauth2.service_account import Credentials
import google.auth.exceptions
import requests
from utils import (
    get_env_setting, DEFAULT_CREDS_FILE, DEFAULT_CREDS_PATH, error
)


# https://docs.gspread.org/

CREDENTIALS = Credentials.from_service_account_file(
    os.path.abspath(
        os.path.join(
            get_env_setting('CREDS_PATH', DEFAULT_CREDS_PATH),
            get_env_setting('CREDS_FILE', DEFAULT_CREDS_FILE),
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

COMMS_ERR_MSG = 'Communications error, check the network connection'


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
        error(
            'Google Sheets error, functionality unavailable\n'\
            'Please check the network connection'
        )

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
        name: str, spreadsheet: gspread.spreadsheet.Spreadsheet = None,
        create: bool = False
    ) -> Union[gspread.worksheet.Worksheet, None]:
    """
    Check is a worksheet with the specified name exists

    Args:
        name (str): worksheet name
        spreadsheet (gspread.spreadsheet.Spreadsheet): spreadsheet to check;
                                                    default global spreadsheet
        create (bool): create if does not exist; default False

    Returns:
        gspread.worksheet.Worksheet: worksheet if exists otherwise None
    """
    if spreadsheet is None:
        spreadsheet = init_spreadsheet()

    the_sheet = None

    if spreadsheet:
        try:
            for sheet in spreadsheet.worksheets():
                if sheet.title == name:
                    the_sheet = sheet
                    break

            if not the_sheet and create:
                the_sheet = add_sheet(name)

        except requests.exceptions.RequestException:
            error(COMMS_ERR_MSG)

    return the_sheet


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
        spreadsheet = init_spreadsheet()

    # TODO specify num column & rows to not waste cells

    worksheet = None
    if spreadsheet:
        try:
            worksheet = spreadsheet.add_worksheet(name, 1000, 26)

        except requests.exceptions.RequestException:
            error(COMMS_ERR_MSG)

    return worksheet
