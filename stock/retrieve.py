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
    'User-Agent': f'analastock/0.0.1 ({platform.system()}/{platform.release()})'
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

SAMPLE_STOCK_PARAM = StockParam.stock_param_of(
    'ibm', datetime(2022, 2, 1), datetime(2022, 3, 1)
)
SAMPLE_DATA = [
    '2022-02-01,133.759995,135.960007,132.500000,135.529999,132.311874,6206400',
    '2022-02-02,135.699997,137.559998,135.259995,137.250000,133.991028,5357200',
    '2022-02-03,137.000000,138.759995,135.830002,137.779999,134.508453,6100800',
    '2022-02-04,137.860001,138.820007,136.220001,137.149994,133.893402,4142000',
    '2022-02-07,137.449997,137.820007,136.270004,137.240005,133.981277,3759000',
    '2022-02-08,137.229996,137.520004,135.779999,137.020004,133.766510,4181800',
    '2022-02-09,137.839996,138.350006,136.830002,137.789993,134.518204,5393500',
    '2022-02-10,135.470001,136.559998,133.169998,133.520004,131.919739,5978600',
    '2022-02-11,133.899994,134.710007,132.380005,132.690002,131.099686,4176200',
    '2022-02-14,132.589996,132.649994,129.070007,130.149994,128.590118,5345300',
    '2022-02-15,130.639999,131.679993,129.610001,129.940002,128.382645,4394000',
    '2022-02-16,129.449997,130.440002,128.259995,129.179993,127.631744,4875600',
    '2022-02-17,128.050003,128.500000,124.849998,124.970001,123.472214,6797000',
    '2022-02-18,124.940002,125.440002,123.610001,124.349998,122.859642,4609200',
    '2022-02-22,124.199997,125.000000,122.680000,123.919998,122.434792,5349700',
    '2022-02-23,124.379997,124.699997,121.870003,122.070000,120.606972,4086400',
    '2022-02-24,120.000000,122.099998,118.809998,121.970001,120.508171,6563200',
    '2022-02-25,122.050003,124.260002,121.449997,124.180000,122.691681,4460900',
    '2022-02-28,122.209999,123.389999,121.040001,122.510002,121.041695,6757300'
]


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
        f'Downloading {load_param.symbol} data: '
        f'{friendly_date(load_param.from_date)} - '
        f'{friendly_date(load_param.to_date)}'
    )

    data = None
    with requests.session():
        response = http_get(url, headers=header, cookies=cookies)
        if response is not None:
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
                        msg = f"Data doesn't exist for date range "\
                            f"{friendly_date(_epoch_datetime(match.group(1)))}"\
                            f" to "\
                            f"{friendly_date(_epoch_datetime(match.group(2)))}"
                elif response.status_code == 404:
                    # not found, e.g. "404 Not Found: No data found, symbol
                    #                   may be delisted"
                    match = NO_SYMBOL_REGEX.match(response.text)
                    if match:
                        msg = match.group(1)

                error(msg)

    return StockDownload(params, data)


def canned_ibm(
            data_type: str
        ) -> Tuple[StockParam, Union[pd.DataFrame, List[str], StockDownload]]:
    """ Returned canned IBM stock """
    if data_type == 'df':
        data = StockDownload.list_to_frame(SAMPLE_DATA)
    elif data_type == 'sd':
        data = StockDownload(SAMPLE_STOCK_PARAM, data)
    else:
        data = SAMPLE_DATA
    return SAMPLE_STOCK_PARAM, data
