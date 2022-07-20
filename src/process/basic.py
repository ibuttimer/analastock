
from stock import canned_ibm
from sheets import save_data



def process_ibm():
    stock_param, data_frame = canned_ibm()
    save_data(stock_param, data_frame)
