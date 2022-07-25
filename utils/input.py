"""
Input related functions
"""
from enum import IntEnum, auto
from typing import Callable
from .constants import HELP, ABORT
from .output import error, assistance


class InputParam(IntEnum):
    """
    Enum representing parameters for input functionality
    """

    NOT_REQUIRED = auto()
    """ Input is not required """


def get_input(
        user_prompt: str, *args, validate: Callable[[str], bool] = None,
        help_text: str = None
    ) -> str:
    """
    Get user input

    Args:
        user_prompt (str): Input prompt
        *args (InputParam): parameters
        validate (Callable[[str], Union[Any|None]]): validate user input
                                                     returning None if invalid
        help_text (str): help text to display

    Returns:
        str: user input
    """
    if isinstance(validate, InputParam):
        ip_args = [validate]
        ip_args.extend(args)
        validate = None
    else:
        ip_args = args

    required = InputParam.NOT_REQUIRED not in ip_args
    data = None

    while not data:
        data = input(f'{user_prompt}: ')

        if data == HELP:
            data = None
            assistance(help_text if help_text else 'No help available')
            continue

        if data == ABORT:
            break

        if not data:
            if required:
                error('Input required')
            else:
                break
        elif validate:
            data = validate(data)

    return data
