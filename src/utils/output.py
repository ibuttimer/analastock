"""
Output related functions
"""
from termcolor import colored

# use Termcolor for all coloured text output
# https://pypi.org/project/termcolor/

def error(msg: str):
    """
    Display error message

    Args:
        msg (str): error message

    Returns:
        None
    """
    print(
        colored(f'> {msg}', 'red')
    )


def info(msg: str):
    """
    Display info message

    Args:
        msg (str): info message

    Returns:
        None
    """
    print(
        colored(f'- {msg}', 'blue')
    )
