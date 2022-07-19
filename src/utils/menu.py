"""
Menu related functions
"""
import dataclasses
from typing import Callable, Union
from .input import get_input
from .output import error

# https://pylint.pycqa.org/en/latest/user_guide/messages/refactor/too-few-public-methods.html

@dataclasses.dataclass
class MenuEntry:
    """
    Class representing a menu entry
    """

    name: str
    """ Display name """

    func: Callable[[], bool]
    """
    Function to call

    Returns:
        bool: True if processed, otherwise False
    """

    key: Union[str, None]
    """ Selection key """

    is_close: bool
    """ Menu close entry flag """

    def __init__(self, name: str, func: Callable[[], bool], key: Union[str, None] = None):
        """
        Constructor

        Args:
            name (str): display name
            func (Callable[[], bool]): function to call when entry selected
            key (Union[str, None]): key to use to select, if None entry index is used; default None
        """
        self.name = name
        self.func = func
        self.key = key
        self.is_close = False

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(' \
               f'{self.name}, {self.key}, {self.is_close})'

@dataclasses.dataclass
class CloseMenuEntry(MenuEntry):
    """
    Class representing a close menu entry
    """

    def __init__(self, name: str, key: Union[str, None] = None):
        """
        Constructor

        Args:
            name (str): display name
            key (Union[str, None]): key to use to select, if None entry index is used; default None
        """
        super().__init__(name, None, key)
        self.is_close = True


class Menu:
    """
    Class representing a menu
    """

    entries: list
    """ Menu entries """

    is_open: bool
    """ Menu open flag """

    def __init__(self, *args):
        """
        Constructor

        Args:
            *args (list): list of MenuEntry
        """
        self.entries = []
        for entry in args:
            if isinstance(entry, MenuEntry):
                self.entries.append(entry)
        self.is_open = False

    def display(self):
        """
        Display the menu
        """
        for index, entry in enumerate(self.entries):
            print(f'{self._entry_key(entry, index)}. {entry.name}')

    def _entry_key(self, entry: MenuEntry, index: int):
        """
        Get the menu entries key

        Args:
            entry (MenuEntry): menu entry
            index (int): zero-based entry index

        Returns:
            str: key
        """
        return entry.key if entry.key else str(index + 1)

    def _is_valid_selection(self, key: str) -> Union[MenuEntry, None]:
        """
        Check if key is a valid selection

        Args:
            key (str): entered key

        Returns:
            MenuEntry: menu entry if valid selection, otherwise None
        """
        selection: Union[MenuEntry, None] = None
        key = key.lower()

        for index, entry in enumerate(self.entries):
            if self._entry_key(entry, index).lower() == key:
                selection = entry
                break

        return selection


    def process(self):
        """
        Process the menu
        """
        selection: Union[MenuEntry, None] = None

        self.is_open = True

        while self.is_open:
            self.display()
            selection = get_input('Enter selection')

            selection = self._is_valid_selection(selection)
            if selection:
                if selection.is_close:
                    self.is_open = False
                else:
                    selection.func()
            else:
                error('Invalid selection')
