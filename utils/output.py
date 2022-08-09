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
    GREY = 'grey'


class WrapMode(Enum):
    """ Class wrap modes """
    NONE = auto()
    CROP = auto()
    AUTO = auto()


class Spacing(Enum):
    """ Enum representing vertical spacings """
    NONE = 0
    """ Enum representing vertical spacings """
    SMALL = 1
    """ Small spacing """
    MEDIUM = 2
    """ Medium spacing """
    LARGE = 3
    """ Large spacing """


ERROR_PREFIX = '> '
INFO_PREFIX = '- '
HELP_PREFIX = '? '
MAX_ERROR_LEN = MAX_LINE_LEN - len(ERROR_PREFIX) - 1
MAX_INFO_LEN = MAX_LINE_LEN - len(INFO_PREFIX) - 1
MAX_HELP_LEN = MAX_LINE_LEN - len(HELP_PREFIX) - 1


def error(msg: str, wrap: WrapMode = WrapMode.AUTO,
          pre_spc: Spacing = Spacing.NONE, post_spc: Spacing = Spacing.NONE):
    """
    Display error message

    Args:
        msg (str): error message
        wrap (WrapMode): wrap mode; Defaults to WrapMode.AUTO.
        pre_spc (Spacing, optional):
            Spacing to allow before display. Defaults to None.
        post_spc (Spacing, optional):
            Spacing to allow after display. Defaults to Spacing.SMALL.

    Returns:
        None
    """
    _display_msg(msg, ERROR_PREFIX, MAX_ERROR_LEN, Colour.RED, wrap,
                 pre_spc=pre_spc, post_spc=post_spc)


def info(msg: str, wrap: WrapMode = WrapMode.NONE,
         pre_spc: Spacing = Spacing.NONE, post_spc: Spacing = Spacing.NONE):
    """
    Display info message

    Args:
        msg (str): info message
        wrap (WrapMode): wrap mode; Defaults to WrapMode.NONE.
        pre_spc (Spacing, optional):
            Spacing to allow before display. Defaults to None.
        post_spc (Spacing, optional):
            Spacing to allow after display. Defaults to None.

    Returns:
        None
    """
    _display_msg(msg, INFO_PREFIX, MAX_INFO_LEN, Colour.BLUE, wrap,
                 pre_spc=pre_spc, post_spc=post_spc)


def assistance(msg: str, wrap: WrapMode = WrapMode.NONE,
               pre_spc: Spacing = Spacing.NONE,
               post_spc: Spacing = Spacing.NONE):
    """
    Display help message

    Args:
        msg (str): help message
        wrap (WrapMode): wrap mode; Defaults to WrapMode.NONE.
        pre_spc (Spacing, optional):
            Spacing to allow before display. Defaults to None.
        post_spc (Spacing, optional):
            Spacing to allow after display. Defaults to None.

    Returns:
        None
    """
    _display_msg(msg, HELP_PREFIX, MAX_HELP_LEN, Colour.YELLOW, wrap,
                 pre_spc=pre_spc, post_spc=post_spc)


def _display_msg(
        msg: str, prefix: str, max_len: int, colour: Colour, wrap,
        pre_spc: Spacing = Spacing.NONE, post_spc: Spacing = Spacing.NONE):
    """
    Display a message

    Args:
        msg (str): message to display
        prefix (str): line prefix
        max_len (int): max length
        colour (Colour): display colour
        wrap (WrapMode): wrap mode
        pre_spc (Spacing, optional):
            Spacing to allow before display. Defaults to None.
        post_spc (Spacing, optional):
            Spacing to allow after display. Defaults to None.
    """
    spacer(pre_spc)
    lines = msg.split('\n')
    for line in lines:
        wrapped = _wrap(line, max_len, wrap=wrap).split('\n')
        for w_line in wrapped:
            display(f'{prefix}{w_line}', colour=colour)
    spacer(post_spc)


def _assert_len(line: str, max_len: int):
    """
    Assert display line length

    Args:
        line (str): display line
        max_len (int): max length
    """
    assert len(line) < max_len, f'Line too long: {line}\n' \
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
                wrapped = f'{wrapped}{chr(0x0A) if idx > 0 else ""}' \
                          f'{msg[idx:idx + max_len]}'
            msg = wrapped

    return msg


def colorise(msg: str, colour: Colour = None, on_colour: Colour = None) -> str:
    """
    Add colour to a message string

    Args:
        msg (str): message
        colour (Colour, optional): text colour. Defaults to None.
        on_colour (Colour, optional): background colour. Defaults to None.

    Returns:
        None
    """
    return colored(
        msg,
        color=colour.value if colour else None,
        on_color=f'on_{on_colour.value}' if on_colour else None
    )


def display(msg: str, colour: Colour = None, on_colour: Colour = None,
            pre_spc: Spacing = Spacing.NONE, post_spc: Spacing = Spacing.NONE):
    """
    Display message

    Args:
        msg (str): message
        colour (Colour, optional): text colour. Defaults to None.
        on_colour (Colour, optional): background colour. Defaults to None.
        pre_spc (Spacing, optional):
            Spacing to allow before display. Defaults to None.
        post_spc (Spacing, optional):
            Spacing to allow after display. Defaults to None.

    Returns:
        None
    """
    spacer(pre_spc)
    print(
        colorise(msg, colour=colour, on_colour=on_colour)
    )
    spacer(post_spc)


def title(msg: str,
          pre_spc: Spacing = Spacing.NONE, post_spc: Spacing = Spacing.NONE):

    """
    Display a title

    Args:
        msg (str): title to display
        pre_spc (Spacing, optional):
            Spacing to allow before display. Defaults to None.
        post_spc (Spacing, optional):
            Spacing to allow after display. Defaults to None.

    Returns:
        None
    """
    display(f' {msg} ', on_colour=Colour.CYAN, pre_spc=pre_spc,
            post_spc=post_spc)


def spacer(size: Spacing = Spacing.SMALL):
    """
    Standard vertical spacing

    Args:
        size (Spacing): spacing size

    Returns:
        None
    """
    if size is not None and size != Spacing.NONE:
        print('\n' * size.value, end='')
