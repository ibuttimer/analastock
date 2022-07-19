"""
Main entry point for application
"""
from utils import Menu, CloseMenuEntry, MenuEntry
from stock import analyse_stock, analyse_ibm


# Application menu
menu: Menu = Menu(
    MenuEntry('Analyse stock', analyse_stock),
    MenuEntry('Analyse IBM', analyse_ibm),
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
