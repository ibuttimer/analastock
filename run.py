"""
Main entry point for application
"""
from dotenv import load_dotenv
from colorama import init

from utils import Menu, CloseMenuEntry, MenuEntry, MenuOption, info
from process import (
    process_exchanges, company_name_search, process_multi_stock, display_help,
    delete_stock_data
)


load_dotenv('./.env')  # take environment variables from .env.

init()  # init Colorama

# Application menu
menu: Menu = Menu(
    MenuEntry('Stock Analysis', process_multi_stock),
    MenuEntry('Search Company', company_name_search),
    MenuEntry('Update Company Information', process_exchanges),
    MenuEntry('Delete Stock Data', delete_stock_data),
    MenuEntry('Help', display_help),
    CloseMenuEntry('Quit'),
    menu_title='AnalaStock Menu',
    options=MenuOption.OPT_NO_ABORT_ROOT
)


def run_app():
    """ Run the application """

    loop: bool = True
    while loop:
        menu.process()

        loop = menu.is_open

    info('Bye')


if __name__ == "__main__":
    run_app()
