"""
Functions related to file paths
"""
import os
from .constants import DEFAULT_DATA_PATH
from .misc import get_env_setting

SAMPLE_EXCHANGES_DATA = 'sample_exchanges.json'
SAMPLE_COMPANY_DATA = 'sample_{exchange}_exchange.json'


def sample_exchanges_path() -> str:
    """
    Get the path to the sample exchanges file

    Returns:
        str: path to file
    """
    return os.path.abspath(
            os.path.join(
                get_env_setting('DATA_PATH', DEFAULT_DATA_PATH),
                SAMPLE_EXCHANGES_DATA
            )
        )

def sample_exchange_path(exchange: str) -> str:
    """
    Get the path to the sample file for ``exchange``

    Args:
        exchange (str): exchange code

    Returns:
        str: path to file
    """
    return os.path.abspath(
            os.path.join(
                get_env_setting('DATA_PATH', DEFAULT_DATA_PATH),
                SAMPLE_COMPANY_DATA.format(exchange=exchange)
            )
        )
