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

    save_data(stock_param, data_frame)

    analyse_stock(
        data_frame
    )


def process_stock():
    # get stock params
    stock_param = get_stock_param()

    analyse_stock(
        download_data(stock_param)
    )
