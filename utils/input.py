"""
Input related functions
"""
from copy import copy
from enum import IntEnum, auto, Enum
from typing import Any, Callable, List, Union
from .constants import HELP, BACK_KEY, HOME_KEY
from .output import error, assistance, Spacing, spacer


YES_OPTIONS = ['y', 'yes']
NO_OPTIONS = ['n', 'no']
INPUT_FORM = copy(YES_OPTIONS)
INPUT_FORM.extend(NO_OPTIONS)


class ControlCode(Enum):
    CONFIRMED = auto()
    """ User confirmed """
    NOT_CONFIRMED = auto()
    """ User did not confirm """
    HOME = auto()
    """ Go to home """
    BACK = auto()
    """ Go back one level """
    BACK_BACK = auto()
    """ Go back two levels """
    CONTINUE = auto()
    """ Continue """

    def is_end_code(self):
        """ Check if this object is an end code """
        return self in ControlCode.END_CODES

    @staticmethod
    def check_end_code(value: Any) -> bool:
        """ Check if ``value`` is an end code """
        return isinstance(value, ControlCode) and \
            value in ControlCode.END_CODES

    def is_unconfirmed(self):
        """ Check if this object is an end code or not confirmed """
        return self.is_end_code() or self == ControlCode.NOT_CONFIRMED

    @staticmethod
    def key_to_code(key: str) -> Union[Enum, None]:
        """
        Covert the specified string to a ControlCode

        Args:
            key (str): string to convert

        Returns:
            Union[ControlCode, None]: ControlCode or None if invalid
        """
        return key if isinstance(key, ControlCode) else \
            ControlCode.HOME if key == HOME_KEY else \
            ControlCode.BACK if key == BACK_KEY else None


ControlCode.END_CODES = [
    ControlCode.HOME, ControlCode.BACK, ControlCode.BACK_BACK
]


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
        pre_spc: Spacing = Spacing.SMALL, post_spc: Spacing = Spacing.NONE
) -> Union[Any, ControlCode]:
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
        Union[Any, ControlCode]: user input or None if invalid
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

        code = ControlCode.key_to_code(data)
        if code:
            data = code
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
        pre_spc: Spacing = Spacing.SMALL, post_spc: Spacing = Spacing.NONE
) -> ControlCode:
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
        ControlCode: user's choice
    """
    if not help_text:
        yes_options = '|'.join(YES_OPTIONS)
        no_options = '|'.join(NO_OPTIONS)
        help_text = f"Enter '{yes_options}' to confirm, "\
                    f"otherwise '{no_options}'"

    confirmation = None
    while confirmation is None:
        selection = get_input(msg, help_text=help_text, input_form=INPUT_FORM,
                              pre_spc=pre_spc, post_spc=post_spc)

        if isinstance(selection, ControlCode):
            confirmation = selection
        else:
            selection = selection.lower()
            if selection in YES_OPTIONS:
                confirmation = ControlCode.CONFIRMED
            elif selection in NO_OPTIONS:
                confirmation = ControlCode.NOT_CONFIRMED

    return confirmation


def get_int(
        msg: str, validate: Callable[[str], Any] = None,
        help_text: str = None,
        pre_spc: Spacing = Spacing.NONE, post_spc: Spacing = Spacing.NONE
) -> Union[int, ControlCode]:
    """
    Get an integer

    Args:
        msg (str): prompt message
        validate (Callable[[str], Union[Any|None]], optional):
                Validate user input returning None if invalid.
                Defaults to None.
        help_text (str, optional): Help text to display. Defaults to None.
        pre_spc (Spacing, optional):
            Spacing to allow before display. Defaults to None.
        post_spc (Spacing, optional):
            Spacing to allow after display. Defaults to Spacing.SMALL.

    Returns:
        Union[int, ControlCode]: number
    """
    if not help_text:
        help_text = "Enter an integer"

    while True:
        selection = get_input(msg, validate=validate, help_text=help_text,
                              pre_spc=pre_spc, post_spc=post_spc)

        if isinstance(selection, str) and selection.isnumeric():
            selection = int(selection)
        if isinstance(selection, int) or ControlCode.check_end_code(selection):
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
        result = None
        is_ok = num_str.isnumeric()
        if not is_ok:
            error(f'Please enter a number between {min_val} and '
                  f'{max_val} inclusive')
        else:
            result = ControlCode.key_to_code(num_str)
            if result is None:
                if min_val <= int(num_str) <= max_val:
                    result = num_str
                else:
                    error(f'Enter a number between {min_val} and '
                          f'{max_val} inclusive')
        return result

    return func
