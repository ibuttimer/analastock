"""
Unit tests for sheet load functions
"""
import unittest

from sheets import sheet_exists, add_sheet

from .base import TestBase


class TestLoad(TestBase):
    """
    Units tests for sheet load functions
    """

    def test_non_existent_sheet(self):
        """
        Test non-existent worksheet
        """
        self.assertIsNotNone(self.spreadsheet)
        self.assertIsNone(
            sheet_exists(
                'non-existent worksheet', spreadsheet=self.spreadsheet)
        )

    def test_adding_sheet(self):
        """
        Test adding worksheet
        """
        worksheet_name = 'added-worksheet'

        self.assertIsNotNone(self.spreadsheet)
        self.assertIsNone(
            sheet_exists(worksheet_name, spreadsheet=self.spreadsheet)
        )
        sheet = add_sheet(worksheet_name, spreadsheet=self.spreadsheet)
        self.assertIsNotNone(sheet)

        # tidy up
        self.tidy_up_sheets(
            [ (worksheet_name, sheet) ]
        )


if __name__ == '__main__':
    unittest.main()
