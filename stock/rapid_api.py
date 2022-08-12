"""
RapidAPI download related functions
"""
from typing import Tuple

import requests

from utils import (
    info, get_env_setting, load_json_file, file_path, http_get,
    DEFAULT_YAHOO_FINANCE_CREDS_FILE, DEFAULT_YAHOO_FINANCE_CREDS_PATH,
    YAHOO_FINANCE_CREDS_FILE_ENV, YAHOO_FINANCE_CREDS_PATH_ENV,
    rapidapi_read_manager, check_429_func
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

    def operation_func() -> requests.Response:
        api_response = http_get(url, **kwargs, headers=rapid_api_header())
        if api_response:
            if RAPID_QUOTA_LIMIT in api_response.headers and \
                    RAPID_QUOTA_REMAIN in api_response.headers:
                limit = int(api_response.headers[RAPID_QUOTA_LIMIT])
                remaining = int(api_response.headers[RAPID_QUOTA_REMAIN])
                info(f'RapidAPI monthly quota {remaining}/{limit}, '
                     f'{remaining/limit:.0%} remaining')

        return api_response

    rapidapi_read_manager().acquire()
    try:
        response = rapidapi_read_manager()\
            .perform(operation_func, check_func=check_func)
    finally:
        rapidapi_read_manager().release()

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


def check_func(response: requests.Response) -> Tuple[bool, str]:
    """
    Check function for quota exceeded responses

    Args:
        response (): response from API

    Returns:
         Tuple[bool, str]: Tuple of
            True if successful, False to backoff and try again,
            message to display
    """
    success, msg = check_429_func(response)
    if not success:
        msg = f'RapidAPI: {msg}'
    return success, msg
