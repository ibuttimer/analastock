"""
Unit tests for sheet load functions
"""
from typing import List, Tuple
import unittest

import gspread

from sheets import open_spreadsheet, sheet_exists, add_sheet


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
            sheets (List[Tuple[str, gspread.worksheet.Worksheet]]):
                                        sheets to delete
        """
        for name, sheet in sheets:
            self.spreadsheet.del_worksheet(sheet)
            self.assertIsNone(
                sheet_exists(name, spreadsheet=self.spreadsheet)
            )

    def add_sheet(
        self, name: str, del_if_exists: bool = False
    ) -> gspread.worksheet.Worksheet:
        """
        Add a worksheet

        Args:
            name (str): worksheet name
            del_if_exists (bool): delete if exists flag

        Returns:
            gspread.worksheet.Worksheet: worksheet
        """
        if del_if_exists:
            sheet = sheet_exists(name, spreadsheet=self.spreadsheet)
            if sheet:
                self.spreadsheet.del_worksheet(sheet)
                self.assertIsNone(
                    sheet_exists(name, spreadsheet=self.spreadsheet)
                )

        self.assertIsNotNone(self.spreadsheet)
        self.assertIsNone(
            sheet_exists(name, spreadsheet=self.spreadsheet)
        )
        sheet = add_sheet(name, spreadsheet=self.spreadsheet)
        self.assertIsNotNone(sheet)

        return sheet
