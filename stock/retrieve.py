"""
Download related functions
"""
import re
import platform
from datetime import datetime, date
from typing import List, Tuple, Union
import pandas as pd
import requests
from bs4 import BeautifulSoup

from utils import info, error, http_get, friendly_date

from .convert import standardise_stock_param
from .data import StockParam, StockDownload


YAHOO_HISTORY_URL = 'https://finance.yahoo.com/quote/{}/history'
YAHOO_DOWNLOAD_URL = \
            'https://query1.finance.yahoo.com/v7/finance/download/{symbol}?'\
            'period1={from_date}&period2={to_date}&'\
            'interval={interval}&events=history&'\
            'includeAdjustedClose=true'

HEADER = {
    'Connection': 'keep-alive',
    'Expires': '-1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent':
        f'analastock/0.0.1 ({platform.system()}/{platform.release()})'
}

DAILY_FREQ = '1d'
WEEKLY_FREQ = '1wk'
MONTHLY_FREQ = '1mo'

# "400 Bad Request: Data doesn't exist for startDate = 633830400,
#       endDate = 638924400"
NO_DATA_REGEX = re.compile(
        r'^400 Bad Request:.*startDate\s*=\s*(\d+)\s*,\s*endDate\s*=\s*(\d+)')
# "404 Not Found: No data found, symbol may be delisted"
NO_SYMBOL_REGEX = re.compile(r'^404 Not Found:\s*(.*)')


def _get_crumbs_and_cookies(stock):
    """
    get crumb and cookies for historical data csv download from yahoo finance

    Based on
    'Interact with the yahoo finance API using python's requests library'
    by Maik Rosenheinrich from https://maikros.github.io/yahoo-finance-python/

    parameters: stock - short-handle identifier of the company

    returns a tuple of header, crumb and cookie
    """
    crumb = None
    cookies = None

    url = YAHOO_HISTORY_URL.format(stock)
    with requests.session():
        website = http_get(url, headers=HEADER)
        if website:
            soup = BeautifulSoup(website.text, 'lxml')
            crumbs = re.findall('"CrumbStore":{"crumb":"(.+?)"}', str(soup))
            if len(crumbs) > 0:
                crumb = crumbs[0]
            cookies = website.cookies

    return HEADER, crumb, cookies


def _date_time_epoch(date_time: Union[datetime, date]) -> str:
    """
    Convert a datetime to a epoch string

    Args:
        date_time (datetime): datetime to convert

    Returns:
        str: epoch
    """
    if isinstance(date_time, date):
        date_time = datetime(date_time.year, date_time.month, date_time.day)
    return str(int(date_time.timestamp()))


def _epoch_datetime(timestamp: Union[str, int]) -> datetime:
    """
    Convert an epoch to a datetime

    Args:
        timestamp (Union[str, int]): epoch to convert

    Returns:
        datetime: datetime
    """
    if isinstance(timestamp, str):
        timestamp = int(timestamp)
    return datetime.fromtimestamp(timestamp)


def download_data(
        params: StockParam, standardise: bool = True) -> StockDownload:
    """
    Download stock data

    Args:
        params (StockParam): stock parameters
        standardise (bool): standardise params; default True

    Returns:
        StockDownload: downloaded data
    """
    load_param = standardise_stock_param(params) if standardise else params

    header, _, cookies = _get_crumbs_and_cookies(load_param.symbol)

    url = YAHOO_DOWNLOAD_URL.format(
        symbol=load_param.symbol,
        from_date=_date_time_epoch(load_param.from_date),
        to_date=_date_time_epoch(load_param.to_date),
        interval=DAILY_FREQ
    )

    info(
        f"Downloading data for '{load_param.symbol}': "
        f"{friendly_date(load_param.from_date)} - "
        f"{friendly_date(load_param.to_date)}"
    )

    data = None
    status_code = StockDownload.NO_RESPONSE
    with requests.session():
        response = http_get(url, headers=header, cookies=cookies)
        if response is not None:
            status_code = response.status_code

            if response.status_code == 200:
                # data in form
                # 'Date,Open,High,Low,Close,Adj Close,Volume\n'
                # '2022-01-03,134.070007,136.289993,133.630005,136.039993,
                #       132.809769,4605900'

                data = response.text.split('\n')

                data = data[1:]     # drop header row

            elif response.status_code >= 400:
                msg = response.text
                if response.status_code == 400:
                    # no data, e.g. "400 Bad Request: Data doesn't exist for
                    #              startDate = 633830400, endDate = 638924400"
                    match = NO_DATA_REGEX.match(response.text)
                    if match:
                        na_from = friendly_date(
                                        _epoch_datetime(match.group(1)))
                        na_to = friendly_date(_epoch_datetime(match.group(2)))
                        msg = f"Data doesn't exist for date range "\
                            f"{na_from} to {na_to}"
                elif response.status_code == 404:
                    # not found, e.g. "404 Not Found: No data found, symbol
                    #                   may be delisted"
                    match = NO_SYMBOL_REGEX.match(response.text)
                    if match:
                        msg = f"No data found, "\
                              f"symbol '{load_param.symbol}' may be delisted"

                error(msg)

    return StockDownload(params, data, status_code)
