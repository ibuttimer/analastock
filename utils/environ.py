"""
Environment related functions
"""
import os
from typing import Any, Union


def get_env_setting(
        key: str, default_value: Any = None,
        required: bool = False) -> Union[str, Any]:
    """
    Get an environmental variable

    Args:
        key (str): variable name
        default_value (Any, optional):
                Default value if not present. Defaults to None.
        required (bool): Required flag

    Returns:
        Union[str, Any]: variable value or ``default_value`` if not set
    """
    value = default_value

    if key in os.environ:
        value = os.environ[key]
        if not value:
            value = default_value

    if not value and required:
        raise ValueError(
            f"The required setting '{key}' is not specified, "
            f"please set '{key}'")

    return value


def is_truthy(text: Union[str, int]) -> bool:
    """
    Check truthy value of text string

    Args
        text (Union[str, int]): text

    Returns
        bool: Truthy value
    """
    value = text
    if isinstance(text, int) or (isinstance(text, str) and text.isnumeric()):
        value = True if int(text) else False
    elif isinstance(text, str):
        value = True if text.lower() in ['y', 'yes', 'true'] else False
    return value

