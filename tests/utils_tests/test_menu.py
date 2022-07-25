"""
Unit tests for menu functions
"""
import unittest

from utils import Menu, MenuEntry


class TestMenu(unittest.TestCase):
    """
    Unit tests for menu functions
    """

    def empty_func(self) -> bool:
        """
        Empty menu function

        Returns:
            bool: True indicating 'processed'
        """
        return True


    def test_multi_page(self):
        """
        Test multi-page menu
        """
        menu: Menu = Menu(
            *[
                MenuEntry(f'Option {i + 1}', self.empty_func) for i in range(Menu.DEFAULT_ROWS)
            ],
            title='Test MultiPage'
        )
        self.assertEqual(menu.num_pages, 1)

        menu.add_entry(MenuEntry(f'Option {Menu.DEFAULT_ROWS}', self.empty_func))
        self.assertEqual(menu.num_pages, 2)


if __name__ == '__main__':
    unittest.main()
