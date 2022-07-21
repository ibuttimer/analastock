"""
Miscellaneous functions
"""
import os
from typing import Any


def get_env_setting(key: str, default_value: Any = None, required: bool = False) -> Any:
    """
    Get an environmental variable

    Args:
        key (str): variable name
        defaultValue (Any, optional): Default value if not present. Defaults to None.
        required (bool): Required flag

    Returns:
        Any: variable value
    """
    value = default_value

    if key in os.environ:
        value = os.environ[key]
        if not value:
            value = default_value

    if not value and required:
        raise ValueError(f"The required setting '{key}' is not specified, please set '{key}'")

    return value
