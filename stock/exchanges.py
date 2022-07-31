"""
Download related functions
"""
import os
import json

import requests

from utils import (
    info, get_env_setting, DEFAULT_RAPID_CREDS_FILE, DEFAULT_RAPID_CREDS_PATH,
    DEFAULT_DATA_PATH, load_json_file, http_get, sample_exchange_path,
    sample_exchanges_path
)

from .enums import DataMode
from .data import StockDownload


# read credentials file and set headers
HEADER = load_json_file(
    os.path.abspath(
            os.path.join(
                get_env_setting('RAPID_CREDS_PATH', DEFAULT_RAPID_CREDS_PATH),
                get_env_setting('RAPID_CREDS_FILE', DEFAULT_RAPID_CREDS_FILE)
            )
        )
)


RAPID_YAHOO_EXCHANGES_URL = \
    "https://yahoofinance-stocks1.p.rapidapi.com/exchanges"
RAPID_YAHOO_COMPANIES_URL = \
    "https://yahoofinance-stocks1.p.rapidapi.com/companies/list-by-exchange"

RAPID_QUOTA_LIMIT = 'X-RateLimit-Requests-Limit'
RAPID_QUOTA_REMAIN = 'X-RateLimit-Requests-Remaining'


def download_exchanges(data_mode: DataMode = DataMode.LIVE) -> StockDownload:
    """
    Download stock data

    Args
        data_mode (DataMode): data mode

    Returns:
        StockDownload: downloaded data
    """

    info(f'Downloading exchanges '\
        f'{"*sample* " if data_mode == DataMode.SAMPLE else ""}data')

    data = None
    if data_mode == DataMode.LIVE:
        response = get(RAPID_YAHOO_EXCHANGES_URL, headers=HEADER)

        if response:
            # data in form
            # '{"total":76,
            # "offset":0,
            # "results":[{"exchangeCode":"AMS"}, ...],
            # "responseStatus":null}'
            data = json.loads(response.text)
    else:
        data = load_json_file(
                    sample_exchanges_path())

    return StockDownload.download_of(data)


def download_companies(
        exchange: str, data_mode: DataMode = DataMode.LIVE) -> StockDownload:
    """
    Download stock data

    Args:
        exchange (str): exchange code
        data_mode (DataMode): data mode

    Returns:
        StockDownload: downloaded data
    """

    info(f'Downloading '\
        f'{"*sample* " if data_mode == DataMode.SAMPLE else ""}'\
        f'company data for {exchange}')

    data = None
    if data_mode == DataMode.LIVE:
        response = get(RAPID_YAHOO_COMPANIES_URL, headers=HEADER,
                        params={ "ExchangeCode":exchange })

        if response:
            # data in form
            # '{"total":140,
            #   "offset":0,
            #   "results":[{"exchangeCode":"AMS","symbol":"AALB.AS",
            #               "companyName":"AALBERTS NV",
            #               "industryOrCategory":"Industrials"}, ...],
            #   "responseStatus":null}'
            data = json.loads(response.text)
    else:
        data = load_json_file(
                    sample_exchange_path(exchange))

    return StockDownload.download_of(data)


def get(url: str, **kwargs) -> requests.Response:
    """
    Get a response

    Args:
        url (str): url to get response from

    Returns:
        requests.Response: response
    """

    response = http_get(url, **kwargs)
    if response:
        if RAPID_QUOTA_LIMIT in response.headers and \
                RAPID_QUOTA_REMAIN in response.headers:
            limit = int(response.headers[RAPID_QUOTA_LIMIT])
            remaining = int(response.headers[RAPID_QUOTA_REMAIN])
            info(f'API monthly quota {remaining}/{limit}, '\
                f'{remaining/limit:.0%} remaining')

    return response
