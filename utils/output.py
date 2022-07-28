"""
Output related functions
"""
from enum import Enum, auto
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

class WrapMode(Enum):
    """ Class wrap modes """
    NONE = auto()
    CROP = auto()
    AUTO = auto()


ERROR_PREFIX = '> '
INFO_PREFIX = '- '
HELP_PREFIX = '? '
MAX_ERROR_LEN = MAX_LINE_LEN - len(ERROR_PREFIX) - 1
MAX_INFO_LEN = MAX_LINE_LEN - len(INFO_PREFIX) - 1
MAX_HELP_LEN = MAX_LINE_LEN - len(HELP_PREFIX) - 1


def error(msg: str, wrap: WrapMode = WrapMode.AUTO):
    """
    Display error message

    Args:
        msg (str): error message
        wrap (WrapMode): wrap mode; Defaults to WrapMode.AUTO.

    Returns:
        None
    """
    _display_msg(msg, ERROR_PREFIX, MAX_ERROR_LEN, Colour.RED, wrap)


def info(msg: str, wrap: WrapMode = WrapMode.NONE):
    """
    Display info message

    Args:
        msg (str): info message
        wrap (WrapMode): wrap mode; Defaults to WrapMode.NONE.

    Returns:
        None
    """
    _display_msg(msg, INFO_PREFIX, MAX_INFO_LEN, Colour.BLUE, wrap)


def assistance(msg: str, wrap: WrapMode = WrapMode.NONE):
    """
    Display help message

    Args:
        msg (str): help message
        wrap (WrapMode): wrap mode; Defaults to WrapMode.NONE.

    Returns:
        None
    """
    _display_msg(msg, HELP_PREFIX, MAX_HELP_LEN, Colour.YELLOW, wrap)


def _display_msg(
        msg: str, prefix: str, max_len: int, colour: Colour, wrap: WrapMode):
    """
    Display a message

    Args:
        msg (str): message to display
        prefix (str): line prefix
        max_len (int): max length
        colour (Colour): display colour
        wrap (WrapMode): wrap mode
    """
    lines = msg.split('\n')
    for line in lines:
        wrapped = _wrap(line, max_len, wrap=wrap).split('\n')
        for w_line in wrapped:
            display(f'{prefix}{w_line}', colour=colour)


def _assert_len(line: str, max_len: int):
    """
    Assert display line length

    Args:
        line (str): display line
        max_len (int): max length
    """
    assert len(line) < max_len, f'Line too long: {line}\n'\
                                f'Cut-off: {line[max_len:]}'


def _wrap(msg: str, max_len: int, wrap: WrapMode = WrapMode.NONE) -> str:
    """
    Process message wrap

    Args:
        msg (str): message text
        max_len (int): max length
        wrap (WrapMode, optional): wrap mode. Defaults to WrapMode.NONE.

    Returns:
        str: string to display
    """
    if wrap == WrapMode.NONE:
        _assert_len(msg, max_len)
    elif len(msg) > max_len:
        if wrap == WrapMode.CROP:
            msg = f'{msg[:max_len - 3]}...'
        elif wrap == WrapMode.AUTO:
            wrapped = ''
            for idx in range(0, len(msg), max_len):
                # no backslash allow in f-string, use chr(0x0A) for '\n'
                wrapped = f'{wrapped}{chr(0x0A) if idx > 0 else ""}'\
                          f'{msg[idx:idx+max_len]}'
            msg = wrapped

    return msg


def colorise(msg: str, colour: Colour = None, on_colour: Colour = None) -> str:
    """
    Display message

    Args:
        msg (str): message

    Returns:
        None
    """
    return colored(
            msg,
            color = colour.value if colour else None,
            on_color = f'on_{on_colour.value}' if on_colour else None
        )


def display(msg: str, colour: Colour = None, on_colour: Colour = None):
    """
    Display message

    Args:
        msg (str): message

    Returns:
        None
    """
    print(
        colorise(msg, colour=colour, on_colour=on_colour)
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
