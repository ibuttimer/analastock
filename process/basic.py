"""
Processing related functions
"""
from stock import (
    canned_ibm, get_stock_param, download_data,
    analyse_stock, download_exchanges, download_companies
)
from sheets import save_data, get_data, save_exchanges, save_companies
from utils.output import info



def process_ibm():
    stock_param, data_frame = canned_ibm("df")

    save_data(data_frame, stock_param=stock_param)

    data_frame = get_data(stock_param)

    analyse_stock(
        data_frame
    )


def process_stock():
    # get stock params
    stock_param = get_stock_param()

    data = get_data(stock_param)

    data = download_data(stock_param)
    save_data(data)

    analyse_stock(data)


def process_exchanges():
    # get exchanges
    exchanges = save_exchanges(
        download_exchanges()
    )

    for i, exchange in enumerate(exchanges):

        code = exchange['exchangeCode']
        info(f"{i+ 1}/{len(exchanges)}: Processing {code}")

        save_companies(
            download_companies(code)
        )

        break
