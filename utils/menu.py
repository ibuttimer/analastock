"""
Menu related functions
"""
from collections import namedtuple
import dataclasses
from typing import Callable, Union

from .constants import ABORT, PAGE_UP, PAGE_DOWN
from .input import get_input
from .output import error, title


MenuOption = namedtuple("MenuOption", ['key', 'name'])

DEFAULT_MENU_HELP = 'Enter number corresponding to desired option'


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

    def __init__(self, name: str, func: Callable[[], bool] = None, key: Union[str, None] = None):
        """
        Constructor

        Args:
            name (str): display name
            key (Union[str, None]): key to use to select, if None entry index is used; default None
            func (Callable[[], bool]): function to call when entry selected
        """
        super().__init__(name, func, key=key)
        self.is_close = True


class Menu:
    """
    Class representing a menu
    """
    DEFAULT_ROWS: int = 10
    """ Default number of rows to display per menu page """

    NO_OPTIONS: int = 0
    """ No menu options """
    OPT_NO_ABORT_BACK: int = 1
    """ Do not allow abort key to function as back """

    entries: list
    """ Menu entries """
    is_open: bool
    """ Menu open flag """
    title: str
    """ Title to display """
    display_rows: int
    """ Maximum number of rows of display """
    options: int
    """ Menu options: default NO_OPTIONS """
    help_text: str
    """ Menu help text """

    def __init__(
            self, *args, menu_title: str = None, rows: int = DEFAULT_ROWS,
            help_text: str = None, options: int = NO_OPTIONS
    ):
        """
        Constructor

        Args:
            title (str, optional): title to display.
                                    Defaults to None.
            rows (int, optional): maximum number of rows of display.
                                    Defaults to 10.
            *args (list): list of MenuEntry
            help_text (str, optional): Help text to display. Defaults to None.
            options (int, optional): Menu options. Defaults to NO_OPTIONS.
        """
        self.entries = []
        for entry in args:
            self.add_entry(entry)
        self.is_open = False
        self.title = menu_title if menu_title else ''
        self.display_rows = rows
        self.help_text = help_text
        self.options = options
        self._start = 0
        self._end = rows
        self._page_keys = []


    def add_entry(self, entry: MenuEntry) -> bool:
        """
        Add an entry to the menu

        Args:
            entry (MenuEntry): entry to add

        Returns:
            bool: True if added, False otherwise
        """
        pre_len = len(self.entries)
        if isinstance(entry, MenuEntry):
            self.entries.append(entry)
        return pre_len != len(self.entries)


    def display(self):
        """
        Display the menu
        """
        self._page_keys.clear()

        print('\f',end='')
        title(f' {self.title} '
              f'{f"[{self.page}/{self.num_pages}] " if self.multi_page else ""}'
        )

        options = []
        key_width = 1
        for index, entry in enumerate(self.entries):
            if index < self._start:
                continue
            if index < self._end:
                key = self._entry_key(entry, index)
                self._page_keys.append(key)
                options.append(MenuOption(key, entry.name))

                if len(key) > key_width:
                    key_width = len(key)

        for option in options:
            print(f'{option.key:>{key_width}}. {option.name}')


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

            selection = get_input(
                'Enter selection', help_text=self.generate_help()
            )

            if self.up_down_page(selection):
                # page inc/dec processed
                continue

            do_page_check = True    # check selections are on current page
            if selection == ABORT and \
                    not self.options & Menu.OPT_NO_ABORT_BACK:
                # abort to close menu
                selected_entry = self.find_close()
                do_page_check = False   # don't check on current page
            else:
                selected_entry = self._is_valid_selection(selection)

            if selected_entry:

                if do_page_check and selection not in self._page_keys:
                    # selection not on current page, verify correct
                    if not self.check_proceed(
                        f"Selection '{selected_entry.name}' not on current "
                        "page, confirm selection"
                    ):
                        continue

                if selected_entry.is_close:
                    # close menu option chosen
                    self.is_open = False
                    if selected_entry.func:
                        # execute func if available
                        selected_entry.func()
                else:
                    # exe menu function
                    selected_entry.func()
            else:
                error('Invalid selection')


    def check_proceed(self, msg: str) -> bool:
        """
        Check is user wishes to proceed

        Args:
            msg (str): check message

        Returns:
            bool: True if proceed, False otherwise
        """
        proceed = False
        while True:
            selection = get_input(
                msg,
                help_text="Enter 'y' to proceed with selection, otherwise 'n'",
                input_form=['y', 'n']

            )
            selection = selection.lower()
            if selection in ('y', 'yes'):
                proceed = True
                break
            if selection in ('n', 'no'):
                proceed = False
                break

        return proceed


    def up_down_page(self, selection: str) -> bool:
        """
        Process up/down page selection

        Args:
            selection (str): user selection

        Returns:
            bool: True if selection processed, otherwise False
        """
        processed = False

        if self.multi_page:
            # multi-page menu check for page inc/dec
            error_msg = None
            pg_up_down = False
            start = self._start

            if selection == PAGE_UP:
                pg_up_down = True
                start += self.display_rows
                if start >= len(self.entries):
                    error_msg = 'No more pages'

            if selection == PAGE_DOWN:
                pg_up_down = True
                start -= self.display_rows
                if start < 0:
                    error_msg = 'No previous page'

            if pg_up_down:
                processed = True    # selection processed
                if not error_msg:
                    self._start = start
                    self._end = start + self.display_rows

                error(error_msg)

        return processed


    def find_close(self) -> Union[CloseMenuEntry, None]:
        """
        Find the close menu option

        Returns:
            Union[CloseMenuEntry, None]: option or None if not found
        """
        selected_entry = None
        for entry in self.entries:
            if isinstance(entry, CloseMenuEntry):
                selected_entry = entry
                break
        return selected_entry


    @property
    def multi_page(self):
        """
        Is multi-page menu flag

        Returns:
            bool: True if multi-page menu
        """
        return len(self.entries) > self.display_rows

    @property
    def page(self):
        """
        Page menu

        Returns:
            int: current menu page
        """
        return int(self._start / self.display_rows) + 1 if self.multi_page else 1


    @property
    def num_pages(self):
        """
        Page menu

        Returns:
            int: current menu page
        """
        pages = int(len(self.entries) / self.display_rows)
        return pages + 1 if len(self.entries) % self.display_rows else \
                pages if self.multi_page else 1

    def generate_help(self) -> str:
        """ Generate menu help text """
        help_text = self.help_text if self.help_text else DEFAULT_MENU_HELP
        if not help_text.endswith('.'):
            help_text += '.'

        can_cancel = not self.options & Menu.OPT_NO_ABORT_BACK
        if self.multi_page or can_cancel:
            pg_help = f"'{PAGE_UP}'/'{PAGE_DOWN}' to page up/down" if self.multi_page else ""
            cancel_help = f"'{ABORT}' to cancel" if can_cancel else ""

            if self.multi_page and can_cancel:
                extra = f"{pg_help}, or {cancel_help}"
            elif self.multi_page:
                extra = pg_help
            else:
                extra = cancel_help

            help_text = f"{help_text}\nChoose {extra}."

        return help_text
