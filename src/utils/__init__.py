"""
Utils package
"""
from .input import get_input, InputParam
from .output import error
from .menu import MenuEntry, CloseMenuEntry, Menu

__all__ = [
    'get_input',
    'InputParam',

    'error',

    'MenuEntry',
    'CloseMenuEntry',
    'Menu',
]
