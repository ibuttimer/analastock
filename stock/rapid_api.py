"""
RapidAPI download related functions
"""
import requests

from utils import (
    info, get_env_setting, load_json_file, file_path, http_get,
    DEFAULT_YAHOO_FINANCE_CREDS_FILE, DEFAULT_YAHOO_FINANCE_CREDS_PATH,
    YAHOO_FINANCE_CREDS_FILE_ENV, YAHOO_FINANCE_CREDS_PATH_ENV
)


RAPID_HEADER = None

RAPID_QUOTA_LIMIT = 'X-RateLimit-Requests-Limit'
RAPID_QUOTA_REMAIN = 'X-RateLimit-Requests-Remaining'


def rapid_get(url: str, **kwargs) -> requests.Response:
    """
    Get a response

    Args:
        url (str): url to get response from

    Returns:
        requests.Response: response
    """

    response = http_get(url, **kwargs, headers=rapid_api_header())
    if response:
        if RAPID_QUOTA_LIMIT in response.headers and \
                RAPID_QUOTA_REMAIN in response.headers:
            limit = int(response.headers[RAPID_QUOTA_LIMIT])
            remaining = int(response.headers[RAPID_QUOTA_REMAIN])
            info(f'API monthly quota {remaining}/{limit}, '
                 f'{remaining/limit:.0%} remaining')

    return response


def rapid_api_header():
    """
    Get the RapidApi headers

    Returns
        gspread.Client: client
    """
    global RAPID_HEADER
    if RAPID_HEADER is None:
        # read credentials file and set headers
        RAPID_HEADER = load_json_file(
            file_path(
                get_env_setting(
                    YAHOO_FINANCE_CREDS_PATH_ENV,
                    DEFAULT_YAHOO_FINANCE_CREDS_PATH),
                get_env_setting(
                    YAHOO_FINANCE_CREDS_FILE_ENV,
                    DEFAULT_YAHOO_FINANCE_CREDS_FILE)
            )
        )

    return RAPID_HEADER
