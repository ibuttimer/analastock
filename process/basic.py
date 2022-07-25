"""
Processing related functions
"""
from typing import Callable
from stock import (
    canned_ibm, get_stock_param, download_data,
    analyse_stock, download_exchanges, download_companies,
    Company
)
from sheets import (
    save_data, get_sheets_data, save_exchanges, save_companies, search_company,
    check_partial
)
from utils import (
    CloseMenuEntry, Menu, MenuEntry, info, ABORT, get_input, title
)


def process_ibm():
    stock_param, data_frame = canned_ibm("df")

    save_data(data_frame, stock_param=stock_param)

    data_frame = get_sheets_data(stock_param)

    analyse_stock(
        data_frame
    )


def stock_analysis_menu():
    """
    Stock analysis menu
    """
    stock_menu: Menu = Menu(
        MenuEntry('Single stock', process_stock),
        MenuEntry('Multiple stocks', process_stock),
        CloseMenuEntry('Back'),
        menu_title='Stock Analysis Menu'
    )
    loop: bool = True
    while loop:
        stock_menu.process()

        loop = stock_menu.is_open


def process_stock(symbol: str = None) -> bool:
    """
    Process a stock analysis

    Args:
        symbol (str, optional): symbol for stock to process. Defaults to None.

    Returns:
        bool: True if processed, otherwise False
    """
    # get stock params
    stock_param = get_stock_param(symbol=symbol)

    processed = stock_param is not None

    if processed:
        data_frame = get_sheets_data(stock_param)

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

        analyse_stock(data_frame)

    return processed


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


def company_search():
    """
    Perform a company search
    """
    title('Company Search')

    loop: bool = True
    while loop:
        name = get_input(
                'Enter company name',
                help_text=f"Enter name or part of name to search for, '{ABORT}' to cancel"
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
            CloseMenuEntry('Back'),
            menu_title='Company Search Results'
        )

        company_menu.process()
