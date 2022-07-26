"""
Output related functions
"""
from enum import Enum
from termcolor import colored

from .constants import MAX_LINE_LEN

# use Termcolor for all coloured text output
# https://pypi.org/project/termcolor/


class Colour(Enum):
    """ Class representing available text colours """
    RED = 'red'
    GREEN = 'green'
    YELLOW = 'yellow'
    BLUE = 'blue'
    MAGENTA = 'magenta'
    CYAN = 'cyan'
    WHITE = 'white'


ERROR_PREFIX = '> '
INFO_PREFIX = '- '
HELP_PREFIX = '? '
MAX_ERROR_LEN = MAX_LINE_LEN - len(ERROR_PREFIX) - 1
MAX_INFO_LEN = MAX_LINE_LEN - len(INFO_PREFIX) - 1
MAX_HELP_LEN = MAX_LINE_LEN - len(HELP_PREFIX) - 1

def error(msg: str):
    """
    Display error message

    Args:
        msg (str): error message

    Returns:
        None
    """
    _assert_len(msg, MAX_ERROR_LEN)
    display(f'{ERROR_PREFIX}{msg}', colour=Colour.RED)


def info(msg: str):
    """
    Display info message

    Args:
        msg (str): info message

    Returns:
        None
    """
    _assert_len(msg, MAX_INFO_LEN)
    display(f'{INFO_PREFIX}{msg}', colour=Colour.BLUE)


def assistance(msg: str):
    """
    Display help message

    Args:
        msg (str): help message

    Returns:
        None
    """
    lines = msg.split('\n')
    for line in lines:
        _assert_len(line, MAX_HELP_LEN)
        display(f'{HELP_PREFIX}{line}', colour=Colour.YELLOW)


def _assert_len(line: str, max_len: int):
    """
    Assert display line length

    Args:
        line (str): display line
        max_len (int): max length
    """
    # HACK disable for now
    # assert len(line) < max_len, f'Line too long: {line}\nCut-off: {line[max_len:]}'


def display(msg: str, colour: Colour = None, on_colour: Colour = None):
    """
    Display message

    Args:
        msg (str): message

    Returns:
        None
    """
    print(
        colored(
            msg,
            color = colour.value if colour else None,
            on_color = f'on_{on_colour.value}' if on_colour else None
        )
    )


def title(msg: str):
    """
    Display a title

    Args:
        msg (str): title to display

    Returns:
        None
    """
    display(msg, on_colour=Colour.CYAN)
