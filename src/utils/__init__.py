"""
Utils package
"""
from .input import get_input, InputParam
from .output import error, info
from .menu import MenuEntry, CloseMenuEntry, Menu

__all__ = [
    'get_input',
    'InputParam',

    'error',
    'info',

    'MenuEntry',
    'CloseMenuEntry',
    'Menu',
]
