"""
Unit tests for sheet load functions
"""
import os
from typing import List, Tuple
from unittest import TestCase, mock

import gspread

from sheets import open_spreadsheet, sheet_exists, add_sheet
from sheets.spread_ops import spreadsheet_del_worksheet


TEST_SPREADSHEET = 'AnalaStockTest'


class TestBase(TestCase):
    """
    Base class for sheets units tests
    """

    @classmethod
    def setUpClass(cls):
        # https://adamj.eu/tech/2020/10/13/how-to-mock-environment-variables-with-pythons-unittest/
        
        # use LevelQuotaMgr for unit tests as RateQuotaMgr needs to be at
        # about 50% to avoid Google Quota exceeded API errors
        # TODO revisit quota managers
        cls.env_patcher = mock.patch.dict(
                    os.environ, {'QUOTA_MGR': 'LevelQuotaMgr'})
        cls.env_patcher.start()

        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

        cls.env_patcher.stop()

    def setUp(self):
        super().setUp()
        self.assertEqual(os.environ["QUOTA_MGR"], "LevelQuotaMgr")

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
            spreadsheet_del_worksheet(self.spreadsheet, sheet)
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
        self.assertIsNotNone(self.spreadsheet)
        if del_if_exists:
            sheet = sheet_exists(name, spreadsheet=self.spreadsheet)
            if sheet:
                spreadsheet_del_worksheet(self.spreadsheet, sheet)

        self.assertIsNone(
            sheet_exists(name, spreadsheet=self.spreadsheet)
        )
        sheet = add_sheet(name, spreadsheet=self.spreadsheet)
        self.assertIsNotNone(sheet)

        return sheet
