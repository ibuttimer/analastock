"""
Unit tests for sheet load functions
"""
from typing import List, Tuple
import unittest

import gspread

from sheets import open_spreadsheet, sheet_exists


TEST_SPREADSHEET = 'AnalaStockTest'


class TestBase(unittest.TestCase):
    """
    Base class for sheets units tests
    """

    def setUp(self):
        self.spreadsheet = open_spreadsheet(TEST_SPREADSHEET)


    def tidy_up_sheets(self,
                       sheets: List[Tuple[str, gspread.worksheet.Worksheet]]):
        """
        Remove worksheets

        Args:
            sheets (List[Tuple[str, gspread.worksheet.Worksheet]]): sheets to delete
        """
        for name, sheet in sheets:
            self.spreadsheet.del_worksheet(sheet)
            self.assertIsNone(
                sheet_exists(name, spreadsheet=self.spreadsheet)
            )
