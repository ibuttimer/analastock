"""
Download related functions
"""
import json

from utils import info

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
    if data_mode == DataMode.LIVE:
        response = rapid_get(RAPID_YAHOO_META_URL, headers=HEADER,
                        params={ "Symbol": symbol })

        if response:
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
            data = json.loads(response.text)
        # TODO non-200 handling
    # else:
    #     data = load_json_file(
    #                 sample_exchanges_path())

    return StockDownload.download_of(data)
