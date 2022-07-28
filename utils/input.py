"""
Input related functions
"""
from enum import IntEnum, auto
from typing import Any, Callable, List, Union
from .constants import HELP, ABORT
from .output import error, assistance


class InputParam(IntEnum):
    """
    Enum representing parameters for input functionality
    """

    NOT_REQUIRED = auto()
    """ Input is not required """


def get_input(
        user_prompt: str,
        *args,
        validate: Callable[[str], bool] = None,
        help_text: str = None,
        input_form: List[str] = None
    ) -> Union[Any, None]:
    """
    Get user input

    Args:
        user_prompt (str): Input prompt
        *args (InputParam): parameters
        validate (Callable[[str], Union[Any|None]], optional):
                Validate user input returning None if invalid. Defaults to None.
        help_text (str, optional): Help text to display. Defaults to None.
        input_form (List[str], optional):
                List of valid inputs. Defaults to None.

    Returns:
        Union[Any, None]: user input or None if invalid
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
        have_input_form = input_form and len(input_form) > 0

        input_form_str = '|'.join(input_form) if have_input_form else ''
        if help_text:
            input_form_str += f'|{HELP}' if have_input_form else f'{HELP}'

        data = input(
            f'{user_prompt}'\
            f'{f" [{input_form_str}]" if input_form_str else ""}: ')

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


def user_confirm(msg: str, help_text: str = None) -> bool:
    """
    Get user confirmation

    Args:
        msg (str): check message

    Returns:
        bool: True if confirmed, False otherwise
    """
    if not help_text:
        help_text="Enter 'y' to confirm, otherwise 'n'"

    proceed = False
    while True:
        selection = get_input(msg, help_text=help_text,input_form=['y', 'n'])

        selection = selection.lower()
        if selection in ('y', 'yes'):
            proceed = True
            break
        if selection in ('n', 'no'):
            proceed = False
            break

    return proceed
