"""
Processing related functions
"""
from typing import Callable, Union

from pandas import DataFrame
from stock import (
    canned_ibm, get_stock_param, download_data,
    analyse_stock, download_exchanges, download_companies,
    Company, AnalysisRange, DATE_FORM, StockParam, DataMode
)
from sheets import (
    save_data, get_sheets_data, save_exchanges, save_companies, search_company,
    check_partial
)
from utils import (
    CloseMenuEntry, Menu, MenuEntry, info, ABORT, get_input, title
)
from .results import display_single


DATE_ENTRY = 'Date entry'
TEXT_ENTRY = 'Text entry'
PERIOD_MENU_HELP = f"Choose '{DATE_ENTRY}' to specify period by dates, "\
                   f"or '{TEXT_ENTRY}' to specify\n"\
                   f"in the form '1m from {DATE_FORM}'"
SYMBOL_ENTRY = 'Enter stock symbol'
SEARCH_ENTRY = 'Search company'
SYMBOL_MENU_HELP = f"Choose '{SYMBOL_ENTRY}' if the stock symbol is known, or"\
                   f"'{SEARCH_ENTRY}' to search by company name"
COMPANY_SEARCH_HELP = f"Enter name or part of name to search for, "\
                      f"or '{ABORT}' to cancel"

def process_ibm():
    """ Process canned IBM stock """
    stock_param, data_frame = canned_ibm("df")

    # check if canned data is already in sheet
    data_frame = get_sheets_data(stock_param)

    # check for gaps in data
    data_frame = fill_gaps(data_frame, stock_param)

    display_single(
        analyse_stock(
            data_frame, stock_param
        )
    )


def stock_analysis_menu():
    """
    Stock analysis menu

    Returns:
        bool: Truthy if processed, otherwise Falsy
    """
    stock_menu: Menu = Menu(
        MenuEntry('Single stock', process_stock_menu),
        MenuEntry('Multiple stocks', process_stock_menu),
        CloseMenuEntry('Back'),
        menu_title='Stock Analysis Menu'
    )
    loop: bool = True
    while loop:
        stock_menu.process()

        loop = stock_menu.is_open

    return True


def period_entry_menu() -> Union[AnalysisRange, None]:
    """
    Period entry method menu

    Returns:
        AnalysisRange: entry method
    """
    anal_rng: AnalysisRange = None

    def set_date_entry():
        nonlocal anal_rng
        anal_rng = AnalysisRange.DATE

    def set_period_entry():
        nonlocal anal_rng
        anal_rng = AnalysisRange.PERIOD

    period_menu: Menu = Menu(
        CloseMenuEntry(DATE_ENTRY, set_date_entry),
        CloseMenuEntry(TEXT_ENTRY, set_period_entry),
        menu_title='Period Entry Method',
        help_text=PERIOD_MENU_HELP
    )
    loop: bool = True
    while loop:
        period_menu.process()

        loop = period_menu.is_open

    return anal_rng


def process_stock_menu() -> bool:
    """
    Process stock menu

    Returns:
        bool: Truthy if processed, otherwise Falsy
    """
    symbol_menu: Menu = Menu(
        CloseMenuEntry(SYMBOL_ENTRY, process_stock),
        CloseMenuEntry(SEARCH_ENTRY, company_search),
        menu_title='Stock Selection Method',
        help_text=SYMBOL_MENU_HELP
    )
    loop: bool = True
    while loop:
        symbol_menu.process()

        loop = symbol_menu.is_open

    return True


def process_stock(symbol: str = None) -> bool:
    """
    Process a stock analysis

    Args:
        symbol (str, optional): symbol for stock to process. Defaults to None.

    Returns:
        bool: Truthy if processed, otherwise Falsy
    """
    # get stock params
    stock_param = get_stock_param(
        symbol=symbol, anal_rng=AnalysisRange.ASK,
        range_select=period_entry_menu)

    processed = stock_param is not None

    if processed:
        data_frame = get_sheets_data(stock_param)

        # check for gaps in data
        data_frame = fill_gaps(data_frame, stock_param)

        display_single(
            analyse_stock(data_frame, stock_param)
        )

    return processed


def fill_gaps(data_frame: DataFrame, stock_param: StockParam) -> DataFrame:
    """
    Fill gaps in a data frame

    Args:
        data_frame (DataFrame): data frame to process
        stock_param (StockParam): params for stock

    Returns:
        DataFrame: data frame
    """
    # check for gaps in data
    gaps = check_partial(data_frame, stock_param)
    if len(gaps) > 0:
        for gap_param in gaps:
            # save data to sheets
            data = download_data(gap_param)
            save_data(data)

            # add data to data frame
            data_frame = data_frame.append(data.data_frame) \
                if data_frame is not None else data.data_frame

    return data_frame


def process_selected_stock(company: Company) -> Callable[[], bool]:
    """
    Decorator to process stock for the specified company

    Args:
        company (Company): company to process

    Returns:
        Callable[[], bool]: process function
    """
    def process_func() -> bool:
        """
        Process a stock analysis

        Returns:
            bool: True if processed, otherwise False
        """
        return process_stock(company.symbol)

    return process_func


def process_exchanges():
    """
    Download and process, stock exchange and companies information
    """
    # HACK sample data for now
    data_mode = DataMode.SAMPLE

    exchanges = save_exchanges(
        download_exchanges(data_mode=data_mode)
    )

    for i, exchange in enumerate(exchanges):

        code = exchange['exchangeCode']
        info(f"{i+ 1}/{len(exchanges)}: Processing {code}")

        save_companies(
            download_companies(code, data_mode=data_mode)
        )

        break   # HACK so just one exchange for now


def company_search() -> bool:
    """
    Perform a company search

    Returns:
        bool: Truthy if processed, otherwise Falsy
    """
    title('Company Search')

    loop: bool = True

    def end_search():
        """ End search """
        nonlocal loop
        loop = False

    while loop:
        name = get_input(
                'Enter company name',
                help_text=COMPANY_SEARCH_HELP
        )
        if name == ABORT:
            loop = False
            continue

        companies = search_company(name)

        if len(companies) == 0:
            info('No matching results found')
            continue

        company_menu: Menu = Menu(
            *[
                MenuEntry(
                    f'{company.name} [{company.symbol}]',
                    process_selected_stock(company)
                ) for company in companies
            ],
            CloseMenuEntry('Search again'),
            CloseMenuEntry('End search', end_search),
            menu_title='Company Search Results'
        )

        company_menu.process()

    return True
