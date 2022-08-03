"""
Download related functions
"""
from utils import (
    info, error, load_json_string, load_json_file, save_json_file,
    sample_meta_path
)

from .enums import DataMode
from .data import StockDownload
from .rapid_api import rapid_get, HEADER


RAPID_YAHOO_META_URL = \
    "https://yahoofinance-stocks1.p.rapidapi.com/stock-metadata"


def download_meta_data(
        symbol: str, data_mode: DataMode = DataMode.LIVE) -> StockDownload:
    """
    Download stock data

    Args
        symbol (str): stock symbol
        data_mode (DataMode): data mode

    Returns:
        StockDownload: downloaded data
    """

    info(f'Retrieving {symbol} '\
        f'{"*sample* " if data_mode == DataMode.SAMPLE else ""}meta data')

    data = None
    status_code = StockDownload.NO_RESPONSE
    if data_mode in [DataMode.LIVE, DataMode.LIVE_SAVE_SAMPLE]:
        response = rapid_get(RAPID_YAHOO_META_URL, headers=HEADER,
                        params={ "Symbol": symbol })

        if response is not None:
            status_code = response.status_code

            if response.status_code == 200:
                # data in form
                # '{"result":{
                #       ...
                #       "currency":"EUR",
                #       "exchangeTimezoneName":"Europe/Amsterdam",
                #       "exchangeTimezoneShortName":"CEST",
                #       "exchange":"AMS",
                #       "shortName":"NEPI ROCKCASTLE S.A."
                #       "market":"nl_market"
                #       "fullExchangeName":"Amsterdam"
                #       "symbol":"NRP.AS"
                #       ...}
                #   ...}
                data = load_json_string(response.text)
                if data is not None:
                    data = data['result']

                    if data_mode == DataMode.LIVE_SAVE_SAMPLE:
                        save_json_file(
                            sample_meta_path(symbol), data)

            else:
                # api return status_code 500
                error(f"No meta data found for symbol '{symbol}' "\
                      f"[{response.status_code}]")
    else:
        status_code = 200
        data = load_json_file(
                        sample_meta_path(symbol))

    return StockDownload.download_of(data, status_code)
