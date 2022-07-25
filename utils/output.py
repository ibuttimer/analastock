"""
Output related functions
"""
from enum import Enum
from termcolor import colored

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


def error(msg: str):
    """
    Display error message

    Args:
        msg (str): error message

    Returns:
        None
    """
    display(f'> {msg}', colour=Colour.RED)


def info(msg: str):
    """
    Display info message

    Args:
        msg (str): info message

    Returns:
        None
    """
    display(f'- {msg}', colour=Colour.BLUE)


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
        display(f'? {line}', colour=Colour.YELLOW)


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
