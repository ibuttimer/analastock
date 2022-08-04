"""
Processing related functions
"""
from enum import Enum, auto
from typing import Any, Callable, List, Union
import time

from pandas import DataFrame, concat
from stock import (
    canned_ibm, get_stock_param, get_stock_param_symbol,
    get_stock_param_range, download_data,
    analyse_stock, download_exchanges, download_companies,
    Company, AnalysisRange, DATE_FORM, StockParam, DataMode, CompanyColumn
)
from sheets import (
    save_stock_data, get_sheets_data, save_exchanges, save_companies,
    search_company, check_partial
)
from utils import (
    CloseMenuEntry, Menu, MenuEntry, info, ABORT, get_input, title,
    user_confirm, get_int, valid_int_range, save_json_file,
    sample_exchange_path, MAX_MULTI_ANALYSIS
)
from .results import display_multiple, display_single


DATE_ENTRY = 'Date entry'
TEXT_ENTRY = 'Text entry'
PERIOD_MENU_HELP = f"Choose '{DATE_ENTRY}' to specify period by dates, "\
                   f"or '{TEXT_ENTRY}' to specify\n"\
                   f"in the form '1m from {DATE_FORM}'"
SYMBOL_ENTRY = 'Enter stock symbol'
SEARCH_ENTRY = 'Search company'
SYMBOL_MENU_HELP = f"Choose '{SYMBOL_ENTRY}' if the stock symbol is known, or"\
                   f"'{SEARCH_ENTRY}' to search by company name"
COMPANY_SEARCH_HELP = f"Enter company name or part of name to search for, "\
                      f"or '{ABORT}' to cancel"
CLEAR_HELP = "Clear data previously saved"
PAUSE_HELP = "Enter pause in seconds between exchange data downloads"
SAMPLE_HELP = "Save data as samples for reuse"
NUM_STOCKS_HELP = "Enter the number of stocks to analyse"

def process_ibm():
    """ Process canned IBM stock """
    stock_param, data_frame = canned_ibm("df")

    # check if canned data is already in sheet
    data_frame = get_sheets_data(stock_param)

    # check for gaps in data
    data_frame = fill_gaps(data_frame, stock_param)

    if data_frame is not None:
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
        MenuEntry('Multiple stocks', process_multi_stock),
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
        CloseMenuEntry(SEARCH_ENTRY, company_name_search),
        menu_title='Stock Selection Method',
        help_text=SYMBOL_MENU_HELP
    )
    loop: bool = True
    while loop:
        symbol_menu.process()

        loop = symbol_menu.is_open

    return True


def process_multi_stock() -> bool:
    """
    Process multiple stocks

    Returns:
        bool: Truthy if processed, otherwise Falsy
    """
    stock_params = []
    num_stocks = get_int('Enter number of stocks',
                    validate=valid_int_range(1, MAX_MULTI_ANALYSIS),
                    help_text=NUM_STOCKS_HELP)

    for idx in range(num_stocks):
        symbol_menu: Menu = Menu(
            CloseMenuEntry(SYMBOL_ENTRY, get_stock_param_symbol),
            CloseMenuEntry(SEARCH_ENTRY,
                lambda : company_name_search(CompanyAction.RETURN)),
            menu_title=f'Stock Selection Method [{idx + 1}/{num_stocks}]',
            help_text=SYMBOL_MENU_HELP
        )
        selection = None
        loop: bool = True
        while loop:
            selection = symbol_menu.process()

            loop = symbol_menu.is_open

        stock_params.append(
            selection if isinstance(selection, StockParam) else \
                StockParam(selection.symbol)
        )

    first_stock_param = stock_params[0]
    get_stock_param_range(first_stock_param, anal_rng=AnalysisRange.PERIOD)

    analysis = []
    for idx in range(num_stocks):
        stock_param = stock_params[idx]
        if idx > 0:
            stock_param.set_from_date(first_stock_param.from_date)
            stock_param.set_to_date(first_stock_param.to_date)

        data_frame = get_sheets_data(stock_param)

        # check for gaps in data
        data_frame = fill_gaps(data_frame, stock_param)

        if data_frame is not None and not data_frame.empty:
            analysis.append(
                analyse_stock(data_frame, stock_param)
            )

    if len(analysis) > 1:
        display_multiple(analysis)
    else:
        display_single(analysis[0])

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
        symbol=symbol, anal_rng=AnalysisRange.PERIOD,
        range_select=period_entry_menu)

    processed = stock_param is not None

    if processed:
        data_frame = get_sheets_data(stock_param)

        # check for gaps in data
        data_frame = fill_gaps(data_frame, stock_param)

        if data_frame is not None and not data_frame.empty:
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
    full_frame = None

    # check for gaps in data
    gaps = check_partial(data_frame, stock_param)
    if len(gaps) > 0:
        full_frame = data_frame
        for gap_param in gaps:
            # save data to sheets
            data = download_data(gap_param)
            if data:
                save_stock_data(data)

                # add data to data frame
                full_frame = concat([full_frame, data.data_frame]) \
                    if full_frame is not None else data.data_frame
    else:
        full_frame = data_frame

    return full_frame


class CompanyAction(Enum):
    """ Enum representing actions to on company selection """
    PROCESS = auto()
    """ Process for analysis """
    RETURN = auto()
    """ Return company object"""


def stock_selected_func(
        company: Company,
        action: CompanyAction = CompanyAction.PROCESS,
        secondary: Callable[[], None] = None) -> Callable[[], Any]:
    """
    Decorator to process selected company

    Args:
        company (Company): company to process
        action (CompanyAction, optional): action to perform on selection.
                Defaults to CompanyAction.PROCESS.
        secondary (Callable[[], None]): secondary processing

    Returns:
        Callable[[], bool]: process function
    """
    def process_func() -> bool:
        """
        Process a stock analysis

        Returns:
            bool: True if processed, otherwise False
        """
        if action == CompanyAction.PROCESS:
            # process company and continue search
            result = process_stock(company.symbol)
        else:
            # return company and end search
            result = company
        if secondary:
            secondary()
        return result

    return process_func


def process_exchanges():
    """
    Download and process, stock exchange and companies information
    """

    # HACK sample data for now
    data_mode = DataMode.SAMPLE
    #data_mode = DataMode.LIVE

    if user_confirm(
        'This operation may take some time, '\
        'please confirm it is ok to proceed'):

        confirm_each = user_confirm('Confirm each download')
        clear_sheet = user_confirm('Clear existing data', help_text=CLEAR_HELP)
        pause = get_int('Enter inter-exchange pause in seconds',
                        validate=valid_int_range(0, 120), help_text=PAUSE_HELP)
        save_sample = user_confirm('Save as sample data', help_text=SAMPLE_HELP)

        exchanges = download_exchanges(data_mode=data_mode)
        exchanges = save_exchanges(exchanges) \
            if exchanges.response_ok else None

        if exchanges:
            for i, exchange in enumerate(exchanges):

                code = exchange['exchangeCode']

                if confirm_each:
                    if not user_confirm(f'Process {code}'):
                        continue

                info(f"{i+ 1}/{len(exchanges)}: Processing {code}")

                companies_data = download_companies(code, data_mode=data_mode)
                if companies_data.response_ok:

                    companies_list = save_companies(
                                        companies_data, clear_sheet=clear_sheet)
                    clear_sheet = False

                    if save_sample and companies_list:
                        save_json_file(
                            sample_exchange_path(code), companies_list)

                    if pause:
                        time.sleep(pause)


def company_name_search(action: CompanyAction = CompanyAction.PROCESS) -> Any:
    """
    Perform a company search by name

    Args:
        action (CompanyAction, optional): action to perform on selection.
                Defaults to CompanyAction.PROCESS.

    Returns:
        Any: Result of selected option's call function or None
    """
    title('Company Name Search')

    loop: bool = True
    result = None

    def end_search():
        """ End search """
        nonlocal loop
        loop = False

    MenuElement = CloseMenuEntry \
        if action == CompanyAction.RETURN else MenuEntry

    def generate_selected_func(company: Company) -> Callable[[], Any]:
        return stock_selected_func(
            company, action,
            secondary = end_search if action == CompanyAction.RETURN else \
                None
        )

    while loop:
        name = get_input(
                'Enter company name',
                help_text=COMPANY_SEARCH_HELP
        )
        if name == ABORT:
            loop = False
            continue

        companies = search_company(name, col=CompanyColumn.NAME)

        if not companies:
            info('No matching results found')
            continue

        # Note: menu & pagination page sizes must match
        companies.set_page_size(Menu.DEFAULT_ROWS)

        # populate first page
        menu_items = company_menu_items(
            companies.get_current_page(), generate_selected_func, MenuElement)
        if companies.num_pages > 1:
            # add placeholders for other pages
            menu_items.extend([
                None for _ in range(Menu.DEFAULT_ROWS, len(companies.items))
            ])
        # add last items
        menu_items.extend([
            CloseMenuEntry('Search again'),
            CloseMenuEntry('End search', end_search, is_preferred=True),
        ])

        def up_down_hook(menu: Menu, start: int, end: int) -> None:
            if not menu.entries[start]:
                # populated page with menu items
                items = companies.get_page(int(start / Menu.DEFAULT_ROWS) + 1)

                assert len(items) == end - start, 'Page size mismatch'

                menu.entries[start:end] = \
                    company_menu_items(
                        items, generate_selected_func, MenuElement)


        company_menu: Menu = Menu(menu_title='Company Search Results')
        company_menu.set_entries(menu_items)
        company_menu.set_up_down_hook(up_down_hook)

        result = company_menu.process()

    return result


def company_menu_items(
            companies: List[Company],
            selected_func: Callable[[], Any],
            menu_element: Union[CloseMenuEntry, MenuEntry] = MenuEntry
        ) -> List[MenuEntry]:
    """
    Generate menu entries for a list of companies

    Args:
        companies (List[Company]): companies
        selected_func (Callable[[], Any]): call function for selection
        MenuElement (CompanyAction, optional): action to perform on selection.
                Defaults to CompanyAction.PROCESS.

    Returns:
        List[MenuEntry]: menu entries
    """
    return [
            menu_element(
                f'{company.name} [{company.symbol}]',
                selected_func(company)
            ) for company in companies
        ]
