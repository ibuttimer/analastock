"""
Processing related functions
"""
from stock import (
    canned_ibm, get_stock_param, download_data,
    analyse_stock
)
from sheets import save_data



def process_ibm():
    stock_param, data_frame = canned_ibm("df")

    save_data(data_frame, stock_param=stock_param)

    analyse_stock(
        data_frame
    )


def process_stock():
    # get stock params
    stock_param = get_stock_param()

    data = download_data(stock_param)
    save_data(data)

    analyse_stock(data)
