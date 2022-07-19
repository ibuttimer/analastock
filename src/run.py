"""
Main entry point for application
"""
from dotenv import load_dotenv
from utils import Menu, CloseMenuEntry, MenuEntry
from stock import analyse_stock, analyse_ibm
from sheets import load_sheet

load_dotenv('../.env')  # take environment variables from .env.

# Application menu
menu: Menu = Menu(
    MenuEntry('Analyse stock', analyse_stock),
    MenuEntry('Analyse IBM', analyse_ibm),
    MenuEntry('sheet', load_sheet),
    CloseMenuEntry('Quit')
)

def run_app():
    """ Run the application """
    loop: bool = True
    while loop:
        menu.process()

        loop = menu.is_open


if __name__ == "__main__":
    run_app()
