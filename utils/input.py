"""
Input related functions
"""
from enum import IntEnum, auto
from typing import Callable
from .output import error


class InputParam(IntEnum):
    """
    Enum representing parameters for input functionality
    """

    NOT_REQUIRED = auto()
    """ Input is not required """


def get_input(user_prompt: str, *args, validate: Callable[[str], bool] = None) -> str:
    """
    Get user input

    Args:
        user_prompt (str): Input prompt
        *args (InputParam): parameters
        validate: Callable[[str], bool]: validate user input

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

        if not data:
            if required:
                error('Input required')
            else:
                break
        elif validate:
            if not validate(data):
                data = None

    return data
