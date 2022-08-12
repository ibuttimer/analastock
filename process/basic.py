"""
Processing related functions
"""
from enum import Enum, auto
from typing import Any, Callable, List, Union, Type
import time

from pandas import DataFrame, concat
from stock import (
    get_stock_param_range, download_data,
    analyse_stock, download_exchanges, download_companies,
    Company, AnalysisRange, DATE_FORM, StockParam, DataMode, CompanyColumn
)
from sheets import (
    save_stock_data, get_sheets_data, save_exchanges, save_companies,
    search_company, check_partial
)
from utils import (
    CloseMenuEntry, Menu, MenuEntry, ProxyMenuEntry, info, BACK_KEY,
    ControlCode, get_input, title, user_confirm, get_int, valid_int_range,
    save_json_file, sample_exchange_path, MAX_MULTI_ANALYSIS, Spacing
)
from .input import (
    get_stock_param_symbol, get_stock_param, get_stock_param_symbol_or_search,
    multi_stock_marker
)
from .results import display_analysis

DATE_ENTRY = 'Date entry'
TEXT_ENTRY = 'Text entry'
PERIOD_MENU_HELP = f"Choose '{DATE_ENTRY}' to specify period by dates, "\
                   f"or '{TEXT_ENTRY}' to specify\n"\
                   f"in the form '1m from {DATE_FORM}'"
SYMBOL_ENTRY = 'Enter stock symbol'
SEARCH_ENTRY = 'Search company'
SYMBOL_MENU_HELP = f"Choose '{SYMBOL_ENTRY}' if the stock symbol is known, "\
                   f"or '{SEARCH_ENTRY}' to search by company name"
COMPANY_SEARCH_HELP = f"Enter company name or part of name to search for, "\
                      f"or '{BACK_KEY}' to cancel"
CLEAR_HELP = "Clear data previously saved"
PAUSE_HELP = "Enter pause in seconds between exchange data downloads"
SAMPLE_HELP = "Save data as samples for reuse"
NUM_STOCKS_HELP = "Enter the number of stocks to analyse"


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
        result = stock_menu.process()

        loop = stock_menu.is_open

    return result


def period_entry_menu() -> Union[AnalysisRange, None]:
    """
    Period entry method menu

    Returns:
        AnalysisRange: entry method
    """
    result = AnalysisRange.ASK

    def set_date_entry():
        nonlocal result
        result = AnalysisRange.DATE

    def set_period_entry():
        nonlocal result
        result = AnalysisRange.PERIOD

    period_menu: Menu = Menu(
        CloseMenuEntry(DATE_ENTRY, set_date_entry),
        CloseMenuEntry(TEXT_ENTRY, set_period_entry),
        menu_title='Period Entry Method',
        help_text=PERIOD_MENU_HELP
    )
    loop: bool = True
    while loop:
        result = period_menu.process()

        loop = period_menu.is_open

    return result


def process_stock_menu(index: int = None, num_stocks: int = None,
                       symbol_func: Callable[[], Any] = None,
                       search_func: Callable[[], Any] = None) -> Any:
    """
    Process stock menu

    Args:
        index (int): index of multiple stocks. Defaults to None.
        num_stocks (int): number of multiple stocks. Defaults to None.
        symbol_func (Callable[[], Any]):
            Function to call for symbol entry. Defaults to None.
        search_func (Callable[[], Any])
            Function to call for symbol search. Defaults to None.

    Returns:
        Any: Truthy if processed, otherwise Falsy
    """
    if symbol_func is None:
        symbol_func = process_stock
    if search_func is None:
        search_func = company_name_search

    stock_idx = multi_stock_marker(index=index, num_stocks=num_stocks)
    symbol_menu: Menu = Menu(
        CloseMenuEntry(SYMBOL_ENTRY, symbol_func),
        CloseMenuEntry(SEARCH_ENTRY, search_func),
        menu_title=f'Stock Selection Method{stock_idx}',
        help_text=SYMBOL_MENU_HELP
    )
    selection = None
    loop: bool = True
    while loop:
        selection = symbol_menu.process()

        loop = symbol_menu.is_open

    return selection


class MultiLevel(Enum):
    NUM_STOCKS = auto()
    STOCKS = auto()
    PERIOD = auto()
    ANALYSE = auto()
    DONE = auto()


def process_multi_stock() -> Union[bool, ControlCode]:
    """
    Process multiple stocks

    Returns:
        Union[bool, ControlCode]: Truthy if processed, otherwise Falsy
    """
    stock_params = []
    result = None

    title(f'Stock Analysis')

    num_stocks = None
    level = MultiLevel.NUM_STOCKS
    while level != MultiLevel.DONE and result is None:

        if level == MultiLevel.NUM_STOCKS:
            # get number of stocks
            num_stocks = get_int(
                'Enter number of stocks',
                validate=valid_int_range(1, MAX_MULTI_ANALYSIS),
                help_text=NUM_STOCKS_HELP, pre_spc=Spacing.SMALL)
            if ControlCode.check_end_code(num_stocks):
                result = num_stocks
            else:
                level = MultiLevel.STOCKS
            continue

        elif level == MultiLevel.STOCKS:
            # get stock symbols
            for idx in range(num_stocks):
                selection = get_stock_param_symbol_or_search(
                    index=idx, num_stocks=num_stocks)

                if not selection:
                    selection = company_name_search(CompanyAction.RETURN)

                if selection == ControlCode.BACK:
                    level = MultiLevel.NUM_STOCKS
                    break
                if ControlCode.check_end_code(selection):
                    result = selection
                    break

                stock_params.append(
                    selection if isinstance(selection, StockParam) else
                    StockParam(
                        selection.symbol
                        if isinstance(selection, Company) else selection)
                )
            else:
                level = MultiLevel.PERIOD
            continue

        elif level == MultiLevel.PERIOD:
            # get analysis period (same for all)
            stock1_param = stock_params[0]
            stock1_param = get_stock_param_range(
                stock1_param, anal_rng=AnalysisRange.PERIOD)

            if stock1_param == ControlCode.HOME:
                result = stock1_param
            elif stock1_param == ControlCode.BACK:
                level = MultiLevel.STOCKS
            else:
                for idx in range(1, num_stocks):
                    # copy same period to all params
                    stock_params[idx].set_dates(stock1_param)

                level = MultiLevel.ANALYSE
            continue

        elif level == MultiLevel.ANALYSE:
            # analyse stocks and display
            analysis = []
            for idx in range(num_stocks):
                stock_param = stock_params[idx]

                data_frame = get_sheets_data(stock_param)

                # check for gaps in data
                data_frame = fill_gaps(data_frame, stock_param)

                if data_frame is not None and not data_frame.empty:
                    analysis.append(
                        analyse_stock(data_frame, stock_param)
                    )

            result = display_analysis(analysis)
            if not ControlCode.is_end_code(result):
                level = MultiLevel.DONE
            continue

        return result


def get_number_of_stocks() -> Union[int, ControlCode]:
    """
    Process multiple stocks

    Returns:
        Union[bool, ControlCode]: Truthy if processed, otherwise Falsy
    """
    return get_int('Enter number of stocks',
                   validate=valid_int_range(1, MAX_MULTI_ANALYSIS),
                   help_text=NUM_STOCKS_HELP, pre_spc=Spacing.SMALL)


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

    if not ControlCode.is_end_code(stock_param):
        result = ControlCode.CONTINUE

        data_frame = get_sheets_data(stock_param)

        # check for gaps in data
        data_frame = fill_gaps(data_frame, stock_param)

        if data_frame is not None and not data_frame.empty:
            display_analysis(
                analyse_stock(data_frame, stock_param)
            )

    else:
        result = stock_param

    return result


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

    title('Update Company Information')

    # HACK sample data for now
    data_mode = DataMode.SAMPLE
    # data_mode = DataMode.LIVE

    user_input = user_confirm('This operation may take some time, '
                              'please confirm it is ok to proceed')
    if user_input == ControlCode.CONFIRMED:

        choices = {}

        for key, prompt, help_text in [
            ('confirm_each', 'Confirm each download', None),
            ('clear_sheet', 'Clear existing data', CLEAR_HELP),
            ('save_sample', 'Save as sample data', SAMPLE_HELP),
        ]:
            user_input = user_confirm(prompt, help_text=help_text)
            choices[key] = user_input == ControlCode.CONFIRMED
            if user_input.is_end_code():
                break
        else:
            user_input = get_int(
                'Enter inter-exchange pause in seconds',
                validate=valid_int_range(0, 120), help_text=PAUSE_HELP,
                pre_spc=Spacing.SMALL)

        if isinstance(user_input, ControlCode) and user_input.is_end_code():
            return user_input

        choices['pause'] = user_input

        exchanges = download_exchanges(data_mode=data_mode)
        exchanges = save_exchanges(exchanges) \
            if exchanges.response_ok else None

        if exchanges:
            for i, exchange in enumerate(exchanges):

                code = exchange['exchangeCode']

                if choices['confirm_each']:
                    user_input = user_confirm(f'Process {code}')
                    if user_input.is_end_code():
                        break
                    elif user_input == ControlCode.NOT_CONFIRMED:
                        continue

                info(f"{i + 1}/{len(exchanges)}: Processing {code}")

                companies_data = download_companies(code, data_mode=data_mode)
                if companies_data.response_ok:

                    companies_list = save_companies(
                        companies_data, clear_sheet=choices['clear_sheet'])
                    choices['clear_sheet'] = False

                    if choices['save_sample'] and companies_list:
                        save_json_file(
                            sample_exchange_path(code), companies_list)

                    if choices['pause']:
                        time.sleep(choices['pause'])

    return user_input


def company_name_search(action: CompanyAction = CompanyAction.PROCESS) -> Any:
    """
    Perform a company search by name

    Args:
        action (CompanyAction, optional): action to perform on selection.
                Defaults to CompanyAction.PROCESS.

    Returns:
        Any: Result of selected option's call function or None
    """
    result = None

    MenuElement = CloseMenuEntry \
        if action == CompanyAction.RETURN else MenuEntry

    def generate_selected_func(company: Company) -> Callable[[], Any]:
        return stock_selected_func(
            company, action,
            secondary=lambda: ControlCode.CONTINUE
            if action == CompanyAction.RETURN else None
        )

    while result is None:
        title('Company Name Search')

        name = get_input(
            'Enter company name',
            help_text=COMPANY_SEARCH_HELP
        )
        if ControlCode.is_end_code(name):
            result = name
            break

        companies = search_company(name, col=CompanyColumn.NAME)

        if not companies:
            query = '. Are you searching by company name?' \
                if len(name) <= 4 else ''
            info(f'No matching results found{query}')
            continue

        info(f'{companies.num_items} matching results found')

        # Note: menu & pagination page sizes must match
        companies.set_page_size(Menu.DEFAULT_ROWS)

        # populate first page
        menu_items = company_menu_items(
            companies.get_current_page(), generate_selected_func, MenuElement)
        if companies.num_pages > 1:
            # add placeholders for other pages
            menu_items.extend([
                ProxyMenuEntry()
                for _ in range(Menu.DEFAULT_ROWS, len(companies.items))
            ])
        # add last items
        menu_items.extend([
            CloseMenuEntry('Search again', lambda: ControlCode.BACK,
                           is_preferred=True),
            CloseMenuEntry('End search', lambda: ControlCode.HOME),
        ])

        def up_down_hook(menu: Menu, start: int, end: int) -> None:
            """
            Handle menu page up/down
            :param menu: menu
            :param start: start display index
            :param end: end display index
            """
            if not menu.entries[start] or menu.entries[start].is_proxy:
                # populate page with menu items
                items = companies.get_page(int(start / Menu.DEFAULT_ROWS) + 1)

                item_cnt = len(items)
                if end == menu.num_entries:
                    item_cnt += 2   # search and end search entries
                elif end == menu.num_entries - 1:
                    item_cnt += 1   # end search entries

                assert item_cnt == end - start,\
                    f'Page size mismatch: {item_cnt} != {end} - {start}'

                menu.entries[start:start + len(items)] = \
                    company_menu_items(
                        items, generate_selected_func, MenuElement)

        company_menu: Menu = Menu(menu_title='Company Search Results')
        company_menu.set_entries(menu_items)
        company_menu.set_up_down_hook(up_down_hook)

        result = company_menu.process()
        if result == ControlCode.BACK:
            # back from sub level, get search name again
            result = None

    return result


def company_menu_items(
        companies: List[Company],
        selected_func: Callable[[Company], Any],
        menu_element: Type[CloseMenuEntry | MenuEntry] = MenuEntry
) -> List[MenuEntry]:
    """
    Generate menu entries for a list of companies

    Args:
        companies (List[Company]): companies
        selected_func (Callable[[Company], Any]): call function for selection
        menu_element (Type[CloseMenuEntry|MenuEntry], optional):
            action to perform on selection. Defaults to CompanyAction.PROCESS.

    Returns:
        List[MenuEntry]: menu entries
    """
    return [
        menu_element(
            f'{company.name} [{company.symbol}]',
            selected_func(company)
        ) for company in companies
    ]
