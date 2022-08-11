"""
Output related functions
"""
import re
from enum import Enum, auto
from typing import Generator, Union

from termcolor import colored

from .constants import MAX_LINE_LEN, MAX_SCREEN_HEIGHT
from .environ import get_env_setting, is_truthy

# use Termcolor for all coloured text output
# https://pypi.org/project/termcolor/

# regex to find formatted text in raw help string
FORMATTING = re.compile(r'{(.*?):?([<>^]?):?(\w+)}')


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

    @staticmethod
    def from_text(text: str) -> Union[Enum, None]:
        """ Get Colour corresponding to specified text """
        text = text.strip().lower()
        result = None
        for val in Colour:
            if text == val.value:
                result = val
                break
        return result


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
LOG_PREFIX = '# '
MAX_ERROR_LEN = MAX_LINE_LEN - len(ERROR_PREFIX) - 1
MAX_INFO_LEN = MAX_LINE_LEN - len(INFO_PREFIX) - 1
MAX_HELP_LEN = MAX_LINE_LEN - len(HELP_PREFIX) - 1
MAX_LOG_LEN = MAX_LINE_LEN - len(LOG_PREFIX) - 1

LOG_ENABLE = is_truthy(get_env_setting('LOGGING', default_value=0))


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


def log(msg: str):
    """
    Display a log message

    Args:
        msg (str): title to display

    Returns:
        None
    """
    if LOG_ENABLE:
        _display_msg(msg, LOG_PREFIX, MAX_LOG_LEN, Colour.WHITE, WrapMode.AUTO)


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
          pre_spc: Spacing = Spacing.LARGE, post_spc: Spacing = Spacing.NONE):
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


def display_paginated(
        generator: Generator[str, None, None],
        page_height: int = MAX_SCREEN_HEIGHT,
        comment: str = '#',
        pre_spc: Spacing = Spacing.NONE, post_spc: Spacing = Spacing.NONE):
    """
    Display paginated text

    Args:
        generator (Generator): content generator
        page_height (int): page height
        comment (str, optional):  ignored line indicator. Defaults to '#'.
        pre_spc (Spacing, optional):
            Spacing to allow before display. Defaults to None.
        post_spc (Spacing, optional):
            Spacing to allow after display. Defaults to None.

    Returns:
        None
    """
    line_num = 0
    for line in generator:
        if line_num % page_height == 0:
            spacer(pre_spc)

        if not line.startswith(comment):
            print(format_line(line), end='')
            line_num += 1

        if line_num % page_height + post_spc.value + 1 == page_height:
            wait_for_next('Press enter for next page', post_spc)

    lfs = page_height - (line_num % page_height + post_spc.value + 1)
    if lfs:
        print('\n' * lfs, end='')

    wait_for_next('Press enter to end', post_spc)


def format_line(line: str) -> str:
    """
    Format a help text line

    Args:
        line (str): raw text

    Returns:
        str: formatted test
    """
    replacements = []

    match = re.findall(FORMATTING, line)
    if match:
        # e.g. [('AnalaStock Help', '^', 'green')]
        for entry in match:
            text = entry[0]
            if entry[1]:
                text = f'{text:{f"{entry[1]}{MAX_LINE_LEN}"}}'
            if entry[2]:
                text = colorise(text, colour=Colour.from_text(entry[2]))
            replacements.append((entry, text))

    result = line
    for elements, replace in replacements:
        colour = f':{elements[2]}' if {elements[2]} else ''
        result = result.replace(f'{{{elements[0]}:'
                                f'{elements[1]}'
                                f'{colour}}}', replace)

    return result


def wait_for_next(msg: str, spacing: Spacing = Spacing.NONE):
    """
    Wait for user input

    Args:
        msg (str): message to display
        spacing (Spacing, optional): spacing before display
    """
    spacer(size=spacing)
    input(msg)
