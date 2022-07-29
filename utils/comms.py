"""
HTTP communications related functions
"""
from typing import Any, Callable
import requests
from .output import error


def _error_msg(exc: requests.exceptions.RequestException):
    """
    Generate an error message to display to the user

    Args:
        exc (requests.exceptions.RequestException): exception

    Returns:
        str: error message
    """
    msg = 'Communications error, please try again later'

    # TODO add logging of actual exception

    if isinstance(exc, requests.exceptions.InvalidJSONError):
        msg = 'Invalid JSON, please try again later'
    elif isinstance(exc, requests.exceptions.HTTPError):
        msg = 'HTTP error, please try again later'
    elif isinstance(exc, requests.exceptions.ConnectionError):
        msg = 'Connection error, please check network connection'
    elif isinstance(exc, requests.exceptions.Timeout):
        msg = 'Timeout error, please try again later'

    return msg


def wrapped_get(func: Callable[[], Any], **kwargs) -> Any:
    """
    Wrap ``func`` to get a response

    Args:
        func (Callable[[], Any]): function to wrap
        **kwargs: Optional arguments that ``func`` takes.

    Returns:
        Any: response
    """

    response = None
    try:
        response = func(**kwargs)

    except requests.exceptions.RequestException as exc:
        error(
            _error_msg(exc)
        )

    return response


def http_get(url: str, **kwargs) -> requests.Response:
    """
    Get a http response

    Args:
        url (str): url to get response from
        **kwargs: Optional arguments that ``request`` takes.

    Returns:
        requests.Response: response
    """

    def get_response() -> requests.Response:
        return requests.get(url, **kwargs)

    return wrapped_get(get_response)
