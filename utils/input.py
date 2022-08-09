"""
Input related functions
"""
from enum import IntEnum, auto
from typing import Any, Callable, List, Union
from .constants import HELP, ABORT
from .output import error, assistance, Spacing, spacer


class InputParam(IntEnum):
    """
    Enum representing parameters for input functionality
    """

    NOT_REQUIRED = auto()
    """ Input is not required """


def get_input(
            user_prompt: str,
            *args,
            validate: Callable[[str], Union[Any, None]] = None,
            help_text: str = None,
            input_form: List[str] = None,
            pre_spc: Spacing = Spacing.NONE, post_spc: Spacing = Spacing.NONE
        ) -> Any:
    """
    Get user input

    Args:
        user_prompt (str): Input prompt
        *args (InputParam): parameters
        validate (Callable[[str], Union[Any, None]], optional):
                Validate user input returning a falsy value if invalid.
                Defaults to None.
        help_text (str, optional): Help text to display. Defaults to None.
        input_form (List[str], optional):
                List of valid inputs. Defaults to None.
        pre_spc (Spacing, optional):
            Spacing to allow before display. Defaults to None.
        post_spc (Spacing, optional):
            Spacing to allow after display. Defaults to Spacing.SMALL.

    Returns:
        Any: user input or None if invalid
    """
    if isinstance(validate, InputParam):
        ip_args = [validate]
        ip_args.extend(args)
        validate = None
    else:
        ip_args = args

    required = InputParam.NOT_REQUIRED not in ip_args
    data = None

    spacer(size=pre_spc)

    while not data:
        have_input_form = input_form and len(input_form) > 0

        input_form_str = '|'.join(input_form) if have_input_form else ''
        if help_text:
            input_form_str += f'|{HELP}' if have_input_form else f'{HELP}'

        data = input(
            f'{user_prompt}'
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

    spacer(size=post_spc)

    return data


def user_confirm(
            msg: str, help_text: str = None,
            pre_spc: Spacing = Spacing.NONE, post_spc: Spacing = Spacing.NONE
        ) -> bool:
    """
    Get user confirmation

    Args:
        msg (str): prompt message
        help_text (str, optional): Help text to display. Defaults to None.
        pre_spc (Spacing, optional):
            Spacing to allow before display. Defaults to None.
        post_spc (Spacing, optional):
            Spacing to allow after display. Defaults to Spacing.SMALL.

    Returns:
        bool: True if confirmed, False otherwise
    """
    if not help_text:
        help_text = "Enter 'y' to confirm, otherwise 'n'"

    while True:
        selection = get_input(msg, help_text=help_text, input_form=['y', 'n'],
                              pre_spc=pre_spc, post_spc=post_spc)

        selection = selection.lower()
        if selection in ('y', 'yes'):
            proceed = True
            break
        if selection in ('n', 'no'):
            proceed = False
            break

    return proceed


def get_int(
            msg: str, validate: Callable[[str], bool] = None,
            help_text: str = None,
            pre_spc: Spacing = Spacing.NONE, post_spc: Spacing = Spacing.NONE
        ) -> int:
    """
    Get an integer

    Args:
        msg (str): prompt message
        validate (Callable[[str], Union[Any|None]], optional):
                Validate user input returning None if invalid. Defaults to None.
        help_text (str, optional): Help text to display. Defaults to None.
        pre_spc (Spacing, optional):
            Spacing to allow before display. Defaults to None.
        post_spc (Spacing, optional):
            Spacing to allow after display. Defaults to Spacing.SMALL.

    Returns:
        int: number
    """
    if not help_text:
        help_text = "Enter an integer"

    while True:
        selection = get_input(msg, validate=validate, help_text=help_text,
                              pre_spc=pre_spc, post_spc=post_spc)

        if isinstance(selection, str) and selection.isnumeric():
            selection = int(selection)
        if isinstance(selection, int):
            value = selection
            break

        error('Enter an integer')

    return value


def valid_int_range(min_val: int, max_val: int) -> Callable[[str], str]:
    """
    Decorator for an entered string validator

    Args:
        min_val (int): min allowed value (inclusive)
        max_val (int): max allowed value (inclusive)

    Returns:
        Callable[[str], str]: function
    """

    def func(num_str: str) -> str | None:
        """
        Validate an entered string is a number within range

        Args:
            num_str (str): enter string

        Returns:
            bool: True if valid
        """
        is_ok = num_str.isnumeric()
        if not is_ok:
            error(f'Please enter a number between {min_val} and '
                  f'{max_val} inclusive')
        else:
            is_ok = min_val <= int(num_str) <= max_val
            if not is_ok:
                error(f'Enter a number between {min_val} and '
                      f'{max_val} inclusive')
        return num_str if is_ok else None

    return func
