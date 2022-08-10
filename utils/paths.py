"""
Functions related to file paths
"""
import os
from .constants import DEFAULT_DATA_PATH, META_DATA_FOLDER
from .environ import get_env_setting

SAMPLE_EXCHANGES_DATA = 'sample_exchanges.json'
SAMPLE_COMPANY_DATA = 'sample_{exchange}_exchange.json'
SAMPLE_META_DATA = 'sample_meta_{symbol}.json'


def file_path(*args) -> str:
    """
    Get the absolute path to a file

    Returns:
        str: path to file
    """
    return os.path.abspath(
        os.path.join(*args)
    )


def sample_exchanges_path() -> str:
    """
    Get the path to the sample exchanges file

    Returns:
        str: path to file
    """
    return file_path(
        get_env_setting('DATA_PATH', DEFAULT_DATA_PATH),
        SAMPLE_EXCHANGES_DATA
    )


def sample_exchange_path(exchange: str) -> str:
    """
    Get the path to the sample companies file for ``exchange``

    Args:
        exchange (str): exchange code

    Returns:
        str: path to file
    """
    return file_path(
        get_env_setting('DATA_PATH', DEFAULT_DATA_PATH),
        SAMPLE_COMPANY_DATA.format(exchange=exchange)
    )


def sample_meta_path(symbol: str) -> str:
    """
    Get the path to the sample meta-data file for ``symbol``

    Args:
        symbol (str): symbol code

    Returns:
        str: path to file
    """
    return file_path(
        get_env_setting('DATA_PATH', DEFAULT_DATA_PATH),
        META_DATA_FOLDER,
        SAMPLE_META_DATA.format(symbol=symbol)
    )
