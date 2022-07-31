"""
Google Sheets related functions
"""
from typing import List, Union
import pandas as pd
from gspread.worksheet import Worksheet
from stock import StockParam, DfColumn, StockDownload, CompanyColumn
from utils import info, EXCHANGES_SHEET, COMPANIES_SHEET
from .load_sheet import sheet_exists
from .utils import updated_range, updated_rows


# https://docs.gspread.org/


def save_data(
        data: Union[pd.DataFrame, StockDownload],
        stock_param: StockParam = None):
    """
    Save data for the specified stock

    Args:
        data (Union[pandas.DataFrame, StockDownload]): data to save
        stock_param (StockParam):
                stock parameters if data is DataFrame, ignored otherwise
    """
    if isinstance(data, StockDownload):
        data_frame = data.data_frame
        symbol = data.stock_param.symbol
    else:
        data_frame = data
        symbol = stock_param.symbol

    sheet = sheet_exists(symbol, create=True, cols=len(DfColumn))

    if sheet and not data_frame.empty:
        # data_frame has dates as np.datetime64
        save_frame = pd.DataFrame(data_frame, copy=True)
        # convert to datetime.date objects
        # https://pandas.pydata.org/docs/reference/api/pandas.Series.dt.date.html#pandas.Series.dt.date
        save_frame[DfColumn.DATE.title] = \
            save_frame[DfColumn.DATE.title].dt.date

        values = save_frame.to_numpy(dtype=str).tolist()
        # [
        #   ['2022-02-01', '133.759995', '135.960007', '132.5', '135.529999',
        #    '132.311874', '6206400'],
        #   ....
        # ]
        result = sheet.append_rows(values, value_input_option='USER_ENTERED')

        info(f'Saved {updated_rows(result)} records to {symbol}')


def save_exchanges(data: Union[pd.DataFrame, StockDownload]) -> List[dict]:
    """
    Save data for the exchanges

    Args:
        data (Union[pandas.DataFrame, StockDownload]): data to save

    Returns:
        dict
    """
    if isinstance(data, StockDownload):
        # json object
        # {"exchangeCode":"AMS"}
        data = data.data

    sheet = sheet_exists(EXCHANGES_SHEET, create=True, cols=1, rows=100)

    if sheet and data:
        sheet.clear()
        values = [
            [exchange['exchangeCode']] for exchange in data['results']
        ]
        result = sheet.append_rows(values, value_input_option='USER_ENTERED')

        info(f"Saved {updated_rows(result)} exchange records")

    return data['results'] if data else None


def companies_sheet() -> Worksheet:
    """
    Get the companies worksheet

    Returns:
        Worksheet: companies worksheet
    """
    return sheet_exists(COMPANIES_SHEET, create=True, cols=len(CompanyColumn))


def save_companies(
        data: Union[pd.DataFrame, StockDownload],
        clear_sheet: bool = False) -> List[dict]:
    """
    Save data for companies

    Args:
        data (Union[pandas.DataFrame, StockDownload]): data to save
        clear_sheet (bool): clear sheet. Defaults to False.

    Returns:
        List[dict]: list of companies
    """
    if isinstance(data, StockDownload):
        # json object
        # {"exchangeCode":"AMS","symbol":"AALB.AS","companyName":"AALBERTS NV",
        #  "industryOrCategory":"Industrials"}
        data = data.data

    sheet = companies_sheet()

    if sheet and data:
        if clear_sheet:
            sheet.clear()
        values = [
            [company[attrib] for attrib in company] \
                for company in data['results']
        ]
        result = sheet.append_rows(values, value_input_option='RAW')

        exchange = values[0][CompanyColumn.EXCHANGE.value - 1] \
            if len(values) > 0 else None

        info(f"Saved {updated_rows(result)} company records"\
            f"{f' for {exchange}' if exchange else ''}")

        # some symbols contain '.' which result in them being displayed as
        # hyperlinks
        sheet.batch_format([{
            "range": updated_range(result),
            "format": {
                "hyperlinkDisplayType": "PLAIN_TEXT"
            },
        }])

    return data['results'] if data else None
