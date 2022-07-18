"""
Input related functions
"""
from enum import IntEnum, auto
from .output import error


class InputParam(IntEnum):
    """
    Enum representing parameters for input functionality
    """

    NOT_REQUIRED = auto()
    """ Input is not required """


def get_input(user_prompt: str, *args) -> str:
    """
    Get user input

    Args:
        user_prompt (str): Input prompt
        args (InputParam): parameters

    Returns:
        str: user input
    """
    required = InputParam.NOT_REQUIRED not in args
    data = None

    while not data:
        data = input(f'{user_prompt}: ')

        if not data:
            if required:
                error('Input required')
            else:
                break

    return data
