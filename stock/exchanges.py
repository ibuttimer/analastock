"""
Download related functions
"""
import json

from utils import (
    info, error, load_json_file, load_json_string,
    sample_exchange_path, sample_exchanges_path
)

from .enums import DataMode
from .data import StockDownload
from .rapid_api import rapid_get, HEADER


RAPID_YAHOO_EXCHANGES_URL = \
    "https://yahoofinance-stocks1.p.rapidapi.com/exchanges"
RAPID_YAHOO_COMPANIES_URL = \
    "https://yahoofinance-stocks1.p.rapidapi.com/companies/list-by-exchange"


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
    status_code = StockDownload.NO_RESPONSE
    if data_mode == DataMode.LIVE:
        response = rapid_get(RAPID_YAHOO_EXCHANGES_URL, headers=HEADER)

        if response is not None:
            status_code = response.status_code

            if response.status_code == 200:
                # data in form
                # '{"total":76,
                # "offset":0,
                # "results":[{"exchangeCode":"AMS"}, ...],
                # "responseStatus":null}'
                data = load_json_string(response.text)
            else:
                error(f"Exchange data currently unavailable "\
                      f"[{response.status_code}]")

    else:
        status_code = 200
        data = load_json_file(
                    sample_exchanges_path())

    return StockDownload.download_of(data, status_code)


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
    status_code = StockDownload.NO_RESPONSE
    if data_mode == DataMode.LIVE:
        response = rapid_get(RAPID_YAHOO_COMPANIES_URL, headers=HEADER,
                        params={ "ExchangeCode": exchange })

        if response is not None:
            status_code = response.status_code

            if response.status_code == 200:
                # data in form
                # '{"total":140,
                #   "offset":0,
                #   "results":[{"exchangeCode":"AMS","symbol":"AALB.AS",
                #               "companyName":"AALBERTS NV",
                #               "industryOrCategory":"Industrials"}, ...],
                #   "responseStatus":null}'
                data = load_json_string(response.text)
            else:
                error(f"No data found for exchange '{exchange}' "\
                      f"[{response.status_code}]")
    else:
        status_code = 200
        data = load_json_file(
                    sample_exchange_path(exchange))

    return StockDownload.download_of(data, status_code)
