from typing import Callable, Union

from stock import StockParam, AnalysisRange, get_stock_param_range
from utils import (
    get_input, BACK_KEY, error, InputParam, ControlCode, colorise,
    Colour
)

SYMBOL_HELP = \
    f"Enter symbol for the stock required, " \
    f"or '{BACK_KEY}' to cancel.\n" \
    f"e.g. IBM: International Business Machines Corporation"
SYMBOL_SEARCH_HELP = \
    f"Enter symbol for the stock required, " \
    f"press enter to search,\n"\
    f"or '{BACK_KEY}' to cancel.\n" \
    f"e.g. IBM: International Business Machines Corporation"


def get_stock_param_symbol(symbol: str = None) -> StockParam:
    """
    Get symbol for stock parameters

    Args:
        symbol (str, optional): Stock symbol. Defaults to None.

    Returns:
        StockParam: stock parameters
    """
    stock_param = None

    if not symbol:
        symbol = get_input(
            'Enter stock symbol', validate=validate_symbol,
            help_text=SYMBOL_HELP
        )

    if not ControlCode.check_end_code(symbol):
        stock_param = StockParam(symbol)

    return stock_param


def get_stock_param_symbol_or_search(
        symbol: str = None,
        index: int = None,
        num_stocks: int = None) -> Union[StockParam, ControlCode]:
    """
    Get symbol for stock parameters

    Args:
        symbol (str, optional): Stock symbol. Defaults to None.
        index (int): index of multiple stocks. Defaults to None.
        num_stocks (int): number of multiple stocks. Defaults to None.

    Returns:
        Union[StockParam, ControlCode]: stock parameters
    """
    stock_param = None

    if not symbol:
        stock_idx = multi_stock_marker(index=index, num_stocks=num_stocks)
        symbol = get_input(
            f'Enter stock {colorise("symbol", Colour.BLUE)} or '
            f'press enter to {colorise("search by name", Colour.BLUE)}'
            f'{stock_idx}',
            InputParam.NOT_REQUIRED,
            validate=validate_symbol,
            help_text=SYMBOL_SEARCH_HELP
        )

    if ControlCode.check_end_code(symbol):
        stock_param = symbol
    elif symbol:
        stock_param = StockParam(symbol)

    return stock_param


def get_stock_param(
                symbol: str = None,
                anal_rng: AnalysisRange = AnalysisRange.DATE,
                range_select: Callable[[], AnalysisRange] = None
        ) -> Union[StockParam, ControlCode]:
    """
    Get stock parameters

    Args:
        symbol (str, optional): Stock symbol. Defaults to None.
        anal_rng (AnalysisRange, optional):
                Range entry method. Defaults to AnalysisRange.DATE.
        range_select (Callable[[], AnalysisRange], optional):
                Range entry method select function. Defaults to None.


    Results:
        Union[StockParam, ControlCode]: stock parameters
    """
    stock_param = get_stock_param_symbol(symbol)

    if not ControlCode.check_end_code(symbol) and stock_param is not None:
        stock_param = get_stock_param_range(stock_param, anal_rng, range_select)

    return stock_param


def validate_symbol(symbol: str) -> Union[str, None]:
    """
    Validate a symbol string

    Args:
        symbol (str): input symbol string

    Returns:
        Union[str, None]: string object if valid, otherwise None
    """
    if symbol.startswith('^'):
        error('Analysis of stock indices is not supported')
        symbol = None

    return symbol


def multi_stock_marker(index: int = None, num_stocks: int = None) -> str:
    """
    Get a multi-stock marker

    Args:
        index (int): index of multiple stocks. Defaults to None.
        num_stocks (int): number of multiple stocks. Defaults to None.

    Returns:
        str: marker
    """
    return f' [{index + 1}/{num_stocks}]' if num_stocks > 1 else ''
