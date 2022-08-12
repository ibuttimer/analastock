"""
Menu related functions
"""
from collections import namedtuple
import dataclasses
from enum import IntFlag, Enum
from typing import Any, Callable, List, Tuple, Union

from .constants import BACK_KEY, PAGE_UP, PAGE_DOWN, MAX_LINE_LEN
from .input import get_input, user_confirm, ControlCode
from .output import error, title, Spacing, scrn_print

KeyName = namedtuple("KeyName", ['key', 'name'])

DEFAULT_MENU_HELP = 'Enter number corresponding to desired option'


@dataclasses.dataclass
class MenuEntry:
    """
    Class representing a menu entry
    """

    name: str
    """ Display name """

    func: Callable[[], Any]
    """
    Function to call

    Returns:
        bool: Truthy if processed, otherwise Falsy
    """

    key: Union[str, None]
    """ Selection key """
    is_close: bool
    """ Menu close entry flag """
    is_proxy: bool
    """ Menu entry proxy flag """

    def __init__(
            self, name: str, func: Callable[[], Any],
            key: Union[str, None] = None):
        """
        Constructor

        Args:
            name (str): display name
            func (Callable[[], bool]): function to call when entry selected
            key (Union[str, None]):
                    key to use to select, if None entry index is used;
                    Defaults to None
        """
        self.name = name
        self.func = func
        self.key = key
        self.is_close = False
        self.is_proxy = False

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(' \
               f'{self.name}, {self.key}, {self.is_close})'


@dataclasses.dataclass
class ProxyMenuEntry(MenuEntry):
    """
    Class representing a proxy menu entry
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__('', None)
        self.is_proxy = True


@dataclasses.dataclass
class CloseMenuEntry(MenuEntry):
    """
    Class representing a close menu entry
    """

    is_preferred: bool
    """ Preferred menu close entry flag """

    def __init__(
            self, name: str, func: Callable[[], Any] = None,
            key: Union[str, None] = None, is_preferred: bool = False):
        """
        Constructor

        Args:
            name (str): display name
            key (Union[str, None]):
                    key to use to select, if None entry index is used;
                    default None
            func (Callable[[], bool]): function to call when entry selected
        """
        super().__init__(name, func, key=key)
        self.is_close = True
        self.is_preferred = is_preferred


class MenuOption(IntFlag):
    """ Menu options enum """
    NO_OPTIONS = 0
    """ No menu options """
    OPT_NO_BACK = 0x01
    """ Do not allow back key """
    OPT_ROOT = 0x02
    """ Root menu """
    OPT_ANY_BACK = 0x04
    """ No specific back menu option """

    OPT_NO_ABORT_ROOT = OPT_ROOT | OPT_NO_BACK
    """ Root menu not allowing abort key to function as back """


class Menu:
    """
    Class representing a menu
    """
    DEFAULT_ROWS: int = 10
    """ Default number of rows to display per menu page """

    entries: list
    """ Menu entries """
    is_open: bool
    """ Menu open flag """
    is_root: bool
    """ Menu root flag """
    title: str
    """ Title to display """
    display_rows: int
    """ Maximum number of rows of display """
    options: int
    """ Menu options: default NO_OPTIONS """
    help_text: str
    """ Menu help text """
    up_down_hook: Callable[[object, int, int], None]
    """
    Function to call on page up/down with signature:
        up_down_hook(menu: Menu, start: int, end: int)
    """

    def __init__(
            self, *args, menu_title: str = None, rows: int = DEFAULT_ROWS,
            help_text: str = None, options: MenuOption = MenuOption.NO_OPTIONS
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
        self.is_root = False
        self.title = menu_title if menu_title else ''
        self.display_rows = rows
        self.help_text = help_text
        self.options = options
        self.up_down_hook = None
        self._start = 0  # index of first item to display
        self._end = rows  # index of last item to display (excluded)
        self._page_keys = []  # keys for the currently displayed page

    def set_entries(self, entries: List[MenuEntry]):
        """
        Set the menu entries

        Args:
            entries (List[MenuEntry]): entries to set
        """
        self.entries = entries

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

        multi_page = \
            f" [{self.page}/{self.num_pages}]" if self.multi_page else ""
        title(f'{self.title}{multi_page}')

        options = []
        key_width = 1
        for index, entry in enumerate(self.entries):
            if index < self._start:
                continue
            if index < self._end:
                key = self._entry_key(entry, index)
                self._page_keys.append(key)
                options.append(KeyName(key, entry.name))

                if len(key) > key_width:
                    key_width = len(key)

        for option in options:
            scrn_print(f'{option.key:>{key_width}}. {option.name}')

    @staticmethod
    def _entry_key(entry: MenuEntry, index: int):
        """
        Get the menu entries key

        Args:
            entry (MenuEntry): menu entry
            index (int): zero-based entry index

        Returns:
            str: key
        """
        return entry.key if entry.key else str(index + 1)

    def _is_valid_selection(
            self, key: str) -> Union[Tuple[MenuEntry, int], None]:
        """
        Check if key is a valid selection

        Args:
            key (str): entered key

        Returns:
            Tuple[MenuEntry, int]:
            MenuEntry: menu entry if valid selection, otherwise None
        """
        selection: Union[MenuEntry, None] = None
        sel_index = None
        key = key.lower()

        for index, entry in enumerate(self.entries):
            if self._entry_key(entry, index).lower() == key:
                selection = entry
                sel_index = index
                break

        return selection, sel_index

    def process(self) -> Any:
        """
        Process the menu

        Returns:
            Any: Result of selected option's call function or None
        """
        result = None

        self.is_open = True
        display_menu = True

        while self.is_open:
            if display_menu:
                self.display()
            # else error occurred don't redisplay
            display_menu = True

            selection = get_input(
                'Enter selection', help_text=self.generate_help(),
                pre_spc=Spacing.NONE
            )

            # process page up/down
            processed, display_menu = self.up_down_page(selection)
            if processed:
                # page inc/dec processed
                continue

            # process menu selection
            result, do_page_check = self._process_user_input(selection)
            if result == ControlCode.HOME:
                # go straight home
                continue
            elif isinstance(result, MenuEntry):
                # ControlCode.BACK will find close entry
                selected_entry = result
            else:
                selected_entry, sel_index = self._is_valid_selection(selection)
                if selected_entry and selected_entry.is_proxy:
                    # selected entry is a proxy so populated it
                    selected_entry = self.process_proxy(sel_index)

            if selected_entry:
                if do_page_check and selection not in self._page_keys:
                    # selection not on current page, verify correct
                    proceed_msg = \
                        f"Selection '{selected_entry.name}'<lf>is not on "\
                        f"current page, confirm selection"
                    if len(proceed_msg) > MAX_LINE_LEN - 5:
                        proceed_msg = proceed_msg.replace('<lf>', '\n')
                    else:
                        proceed_msg = proceed_msg.replace('<lf>', ' ')

                    confirmation = Menu.check_proceed(proceed_msg)
                    if confirmation in [
                        ControlCode.NOT_CONFIRMED, ControlCode.HOME
                    ]:
                        continue
                    elif confirmation == ControlCode.BACK:
                        selected_entry = self.find_back_if_allowed()
                    # else process selection

                if selected_entry.is_close:
                    # close menu option chosen
                    self.is_open = False

                if selected_entry.func:
                    # execute func if available
                    result = selected_entry.func()
                    if result == ControlCode.HOME:
                        if MenuOption.OPT_ROOT in self.options:
                            result = ControlCode.CONTINUE
                        break
            else:
                error('Invalid selection')

        return result

    def _process_user_input(
                self, user_input: Union[str, ControlCode]
            ) -> tuple[CloseMenuEntry | None | Enum, bool]:
        """
        Process user input

        Args:
            user_input (Union[str, ControlCode])): user input

        Returns:
             tuple[CloseMenuEntry | None | Enum, bool]:
        """
        do_page_check = True    # check selections are on current page
        result = user_input
        if result == ControlCode.HOME:
            if MenuOption.OPT_ROOT not in self.options:
                # go straight home, close menu
                self.is_open = False
            else:
                error('Not available, root menu')
                result = None
        elif result == ControlCode.BACK:
            result = self.find_back_if_allowed()
            if result:
                do_page_check = False  # don't check on current page

        return result, do_page_check

    @staticmethod
    def check_proceed(msg: str) -> ControlCode:
        """
        Check is user wishes to proceed

        Args:
            msg (str): check message

        Returns:
            ControlCode: user selection
        """
        return user_confirm(
            msg,
            help_text="Enter 'y' to proceed with selection, otherwise 'n'")

    def up_down_page(self, selection: str) -> Tuple[bool, bool]:
        """
        Process up/down page selection

        Args:
            selection (str): user selection

        Returns:
            Tuple[bool, bool]: tuple of
                        True if selection processed, otherwise False
                        True if no error, otherwise False
        """
        processed = False
        error_msg = None

        if self.multi_page:
            # multi-page menu check for page inc/dec
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
                processed = True  # selection processed
                if not error_msg:
                    self._start = start
                    self._end = start + self.display_rows
                    if self._end > self.num_entries:
                        self._end = self.num_entries

                    if self.up_down_hook:
                        # call hook, with display start/end indices
                        self.up_down_hook(self, self._start, self._end)

            if error_msg:
                error(error_msg)

        return processed, error_msg is None

    def process_proxy(self, index: int) -> MenuEntry:
        """
        Process a proxy menu entry

        Args:
            index (int): index of proxy

        Returns:
            MenuEntry: menu entry for specified index
        """
        if self.multi_page:
            # multi-page menu check for page inc/dec
            start = int(index / self.display_rows) * self.display_rows

            if self.up_down_hook:
                # call hook, with process start/end indices
                self.up_down_hook(self, start, start + self.display_rows)

        return self.entries[index]

    def set_up_down_hook(
            self, up_down_hook: Callable[[object, int, int], None]):
        """
        Set the up/down hook function

        Args:
            up_down_hook (Callable[[Menu, int, int], None]): hook function
        """
        self.up_down_hook = up_down_hook

    def find_close(self) -> Union[CloseMenuEntry, None]:
        """
        Find the close menu option

        Returns:
            Union[CloseMenuEntry, None]: option or None if not found
        """
        close_entry = None

        # find all close items
        items = list(
            filter(
                lambda entry: isinstance(entry, CloseMenuEntry), self.entries)
        )
        if len(items) > 1:
            # find preferred close item
            preferred = list(
                filter(lambda entry: entry.is_preferred, items.copy())
            )
            if len(preferred) > 1:
                raise ValueError(
                    f'Multiple preferred close entries found: '
                    f'{len(preferred)}')
            elif len(preferred) == 1:
                close_entry = preferred[0]
            elif MenuOption.OPT_ANY_BACK in self.options:
                close_entry = CloseMenuEntry('AnyBack')
            else:
                # use first close item
                close_entry = items[0]
        elif len(items) == 1:
            close_entry = items[0]

        return close_entry

    def find_back_if_allowed(self) -> Union[CloseMenuEntry, None]:
        """
        Find the back menu option if menu allows back

        Returns:
            Union[CloseMenuEntry, None]: option or None if not found
        """
        result = None
        if MenuOption.OPT_NO_BACK not in self.options:
            # close menu
            result = self.find_close()
        elif MenuOption.OPT_ANY_BACK in self.options:
            result = CloseMenuEntry('AnyBack')
        else:
            error('Back not allowed')

        return result

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
            int: current menu page (1-based)
        """
        return int(self._start / self.display_rows) + 1 \
            if self.multi_page else 1

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

    @property
    def num_entries(self):
        """
        Number of entries

        Returns:
            int: number of entries
        """
        return len(self.entries)

    def generate_help(self) -> str:
        """ Generate menu help text """
        help_text = self.help_text if self.help_text else DEFAULT_MENU_HELP
        if not help_text.endswith('.'):
            help_text += '.'

        can_cancel = MenuOption.OPT_NO_BACK in self.options
        if self.multi_page or can_cancel:
            # append multi-page menu and cancel help
            pg_help = f"'{PAGE_UP}'/'{PAGE_DOWN}' to page up/down" \
                if self.multi_page else ""
            cancel_help = f"'{BACK_KEY}' to cancel" if can_cancel else ""

            if self.multi_page and can_cancel:
                extra = f"{pg_help}, or {cancel_help}"
            elif self.multi_page:
                extra = pg_help
            else:
                extra = cancel_help

            help_text = f"{help_text}\nChoose {extra}."

        return help_text


def pick_menu(
        entries: List[Tuple[str, Any]], menu_title: str = None,
        rows: int = Menu.DEFAULT_ROWS, help_text: str = None,
        options: MenuOption = MenuOption.NO_OPTIONS) -> Any:
    """
    Auto-close menu to pick an option

    Args:
        entries (List[Tuple(str, Any)]):
                list of entries of tuples of text, result
        menu_title (str, optional): title to display.
                                Defaults to None.
        rows (int, optional): maximum number of rows of display.
                                Defaults to 10.
        help_text (str, optional): Help text to display. Defaults to None.
        options (int, optional): Menu options. Defaults to NO_OPTIONS.

    Returns:
        Any: value of selected entry
    """
    result = None

    def choose_func(choice_value: Any):
        def set_choice():
            nonlocal result
            result = choice_value

        return set_choice

    menu: Menu = Menu(menu_title=menu_title, rows=rows, help_text=help_text,
                      options=options)

    for text, value in entries:
        menu.add_entry(
            CloseMenuEntry(text, lambda: value)
        )

    loop: bool = True
    while loop:
        result = menu.process()

        loop = menu.is_open

    return result
