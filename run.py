"""
Main entry point for application
"""
from dotenv import load_dotenv
from colorama import init

from utils import Menu, CloseMenuEntry, MenuEntry, info
from stock import analyse_stock, analyse_ibm
from process import process_ibm

load_dotenv('../.env')  # take environment variables from .env.

init()  # init Colorama

# Application menu
menu: Menu = Menu(
    MenuEntry('Analyse stock', analyse_stock),
    MenuEntry('Analyse IBM', analyse_ibm),
    MenuEntry('Process IBM', process_ibm),
    CloseMenuEntry('Quit')
)

def run_app():
    """ Run the application """

    # process_ibm()

    loop: bool = True
    while loop:
        menu.process()

        loop = menu.is_open

    info('Bye')

if __name__ == "__main__":
    run_app()
