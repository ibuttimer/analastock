"""
Output related functions
"""
import re
import platform
from datetime import datetime
import requests
from bs4 import BeautifulSoup

from .stock_param import StockParam


YAHOO_HISTORY_URL = 'https://finance.yahoo.com/quote/{}/history'
YAHOO_DOWNLOAD_URL = 'https://query1.finance.yahoo.com/v7/finance/download/{symbol}?'\
            'period1={from_date}&period2={to_date}&interval={interval}&events=history&'\
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


SAMPLE_DATA = [
    'Date,Open,High,Low,Close,Adj Close,Volume',
    '2022-01-03,134.070007,136.289993,133.630005,136.039993,132.809769,4605900',
    '2022-01-04,136.100006,139.949997,135.899994,138.020004,134.742767,7300000',
    '2022-01-05,138.309998,142.199997,137.880005,138.220001,134.938019,8956900',
    '2022-01-06,138.199997,138.410004,132.509995,135.339996,132.126389,9908100',
    '2022-01-07,134.899994,135.660004,133.509995,134.830002,131.628494,5238100',
    '2022-01-10,134.470001,136.199997,133.380005,135.029999,131.823746,5432800',
    '2022-01-11,130.520004,133.250000,127.970001,132.869995,129.715042,11105300',
    '2022-01-12,133.250000,134.470001,131.369995,133.589996,130.417938,5352000',
    '2022-01-13,133.899994,136.050003,133.559998,134.759995,131.560150,4868300',
    '2022-01-14,134.550003,135.139999,133.300003,134.210007,131.023224,5310300',
    '2022-01-18,132.949997,133.889999,131.779999,132.940002,129.783386,5246700',
    '2022-01-19,132.899994,133.899994,131.500000,131.580002,128.455673,4103700',
    '2022-01-20,131.259995,132.880005,130.570007,130.820007,127.713730,5278200',
    '2022-01-21,131.649994,131.869995,129.270004,129.350006,126.278625,5907000',
    '2022-01-24,127.989998,129.149994,124.190002,128.820007,125.761215,13484000',
    '2022-01-25,129.139999,137.339996,128.300003,136.100006,132.868362,19715700',
    '2022-01-26,136.470001,137.070007,133.130005,134.259995,131.072037,8336000',
    '2022-01-27,133.660004,134.750000,132.080002,132.520004,129.373367,5497300',
    '2022-01-28,133.190002,134.529999,131.789993,134.500000,131.306351,5471500',
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

    url = YAHOO_HISTORY_URL.format(stock)
    with requests.session():
        website = requests.get(url, headers=HEADER)
        soup = BeautifulSoup(website.text, 'lxml')
        crumb = re.findall('"CrumbStore":{"crumb":"(.+?)"}', str(soup))

        return (HEADER, crumb[0], website.cookies)


def _timestamp_epoch(date_time: datetime) -> str:
    """
    Convert a datetime to a epoch string

    Args:
        date_time (datetime): datetime to convert

    Returns:
        str: epoch
    """
    return str(int(date_time.timestamp()))


def download_data(params: StockParam):
    """
    Download stock data

    Args:
        params (StockParam): stock parameters

    Returns:
        None
    """

    header, crumb, cookies = _get_crumbs_and_cookies(params.symbol)

    url = YAHOO_DOWNLOAD_URL.format(
        symbol=params.symbol, from_date=_timestamp_epoch(params.from_date),
        to_date=_timestamp_epoch(params.to_date), interval=DAILY_FREQ
    )

    with requests.session():
        res = requests.get(url, headers=header, cookies=cookies)

        data = res.text.split('\n')[:-1]

        print(data)
