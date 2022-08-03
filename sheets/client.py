"""
Google Sheets client related functions
"""
import os
import gspread
from google.oauth2.service_account import Credentials
from utils import (
    get_env_setting, DEFAULT_GOOGLE_CREDS_FILE, DEFAULT_GOOGLE_CREDS_PATH,
    GOOGLE_CREDS_FILE_ENV, GOOGLE_CREDS_PATH_ENV
)

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
