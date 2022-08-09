"""
Main entry point for application
"""
from dotenv import load_dotenv
from colorama import init

from utils import Menu, CloseMenuEntry, MenuEntry, info
from process import (
    process_ibm, stock_analysis_menu, process_exchanges, company_name_search,
    process_multi_stock
)


load_dotenv('./.env')  # take environment variables from .env.

init()  # init Colorama

# Application menu
menu: Menu = Menu(
    MenuEntry('Stock Analysis', process_multi_stock),
    # MenuEntry('Process IBM', process_ibm),
    MenuEntry('Search Company', company_name_search),
    MenuEntry('Update Company Information', process_exchanges),
    CloseMenuEntry('Quit'),
    menu_title='AnalaStock Menu',
    options=Menu.OPT_NO_ABORT_BACK
)


def run_app():
    """ Run the application """

    # HACK process_ibm
    # process_ibm()

    loop: bool = True
    while loop:
        menu.process()

        loop = menu.is_open

    info('Bye')


if __name__ == "__main__":
    run_app()
