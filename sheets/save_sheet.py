"""
Google Sheets related functions
"""
from typing import List, Union
import pandas as pd
from gspread.utils import a1_range_to_grid_range
from stock import (
    StockParam, DfColumn, StockDownload, CompanyColumn, ExchangeColumn
)
from stock.data import Company
from utils import info, error, EXCHANGES_SHEET, drill_dict
from .load_sheet import (
    sheet_exists, companies_sheet, eft_sheet, mutual_sheet, future_sheet,
    index_sheet
)
from .search import search_meta
from .utils import updated_range, updated_rows, cells_range
from .spread_ops import (
    sheet_append_row, sheet_append_rows, sheet_batch_update, sheet_clear,
    sheet_batch_format
)


# https://docs.gspread.org/


def save_stock_data(
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
        if not data.response_ok:
            return

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
        result = sheet_append_rows(
                    sheet, values, value_input_option='USER_ENTERED')

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
        if not data.response_ok:
            return None

        data = data.data

    sheet = sheet_exists(
        EXCHANGES_SHEET, create=True,
        cols=len(ExchangeColumn), rows=len(data['results']) + 5)

    if sheet and data:
        sheet_clear(sheet)
        values = [
            [exchange['exchangeCode']] for exchange in data['results']
        ]
        result = sheet_append_rows(
                    sheet, values, value_input_option='USER_ENTERED')

        info(f"Saved {updated_rows(result)} exchange records")

    return data['results'] if data else None


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
        if not data.response_ok:
            return None

        data = data.data

    sheet = companies_sheet()

    if sheet and data:
        if clear_sheet:
            sheet_clear(sheet)
        values = [
            [company[attrib] for attrib in company]
            for company in data['results']
        ]
        result = sheet_append_rows(sheet, values, value_input_option='RAW')

        exchange = values[0][CompanyColumn.EXCHANGE.value - 1] \
            if len(values) > 0 else None

        info(f"Saved {updated_rows(result)} company records"
             f"{f' for {exchange}' if exchange else ''}")

        # some symbols contain '.' which result in them being displayed as
        # hyperlinks
        sheet_batch_format(sheet, [{
            "range": updated_range(result),
            "format": {
                "hyperlinkDisplayType": "PLAIN_TEXT"
            },
        }])

    return data['results'] if data else None


def save_stock_meta_data(
        symbol: str,
        currency: str = None,
        name: str = None,
        meta: dict = None) -> List[dict]:
    """
    Save data for companies

    Args:
        symbol (str): stock symbol
        currency (str, optional): stock currency. Default to None.
        name (str, optional): company name. Default to None.
        meta (dict, optional): meta data. Default to None.
    """
    if not currency and not name:
        return  # nothing to do

    error_msg = None

    # determine stock type
    quote_type = meta["quoteType"].upper() if meta else "EQUITY"
    if quote_type == "ETF":
        # Exchange Traded Fund
        sheet = eft_sheet()
    elif quote_type == "MUTUALFUND":
        # Mutual Fund
        sheet = mutual_sheet()
    elif quote_type == "FUTURE":
        # Futures
        sheet = future_sheet()
    elif quote_type == "INDEX":
        # Index
        sheet = index_sheet()
    else:
        # default equity
        sheet = companies_sheet()

    # attempt to find symbol on entity page
    pg_result = search_meta(
        symbol.upper(), CompanyColumn.SYMBOL, sheet, exact_match=True
    )
    if pg_result and pg_result.num_items >= 1:
        if pg_result.num_items == 1:
            # get data range, e.g. 'A1:E1'
            page = pg_result.get_current_page(transform=False)
            assert len(page) == 1
            # Note: all indexes are zero-based
            # {'startRowIndex': 0, 'endRowIndex': 1, 'startColumnIndex': 0,
            #   'endColumnIndex': 1}
            entity_row = \
                a1_range_to_grid_range(page[0])['startRowIndex'] + 1

            updates = []

            if currency:
                # update currency
                # Note: rows/cols are 1-based
                updates.append((CompanyColumn.CURRENCY.value, currency))

            if name:
                # update name
                updates.append((CompanyColumn.NAME.value, name))

            if len(updates) > 0:
                sheet_batch_update(sheet, [
                    range_update(
                        cells_range(
                            entity_row, col,
                            entity_row, col
                        ), value
                    ) for col, value in updates
                ], value_input_option='RAW')

        else:
            error_msg = f"Multiple '{symbol}' entries: data not saved"
    else:
        # add the metadata to the sheet
        values = Company.company_of(
                drill_dict(meta, "exchange"), symbol,
                drill_dict(meta, "shortName"), None,
                drill_dict(meta, "currency")
            ).unpack()

        sheet_append_row(sheet, values, value_input_option='RAW')

    if error_msg:
        error(error_msg)


def range_update(cell_rng: str, values: List[List]):
    """
    Generate batch_update entry

    Args:
        cell_rng (str): cells range
        values (List[List]): values to update

    Returns:
        object: entry
    """
    return {
        'range': cell_rng,
        'values': [values if isinstance(values, list) else [values]]
    }
