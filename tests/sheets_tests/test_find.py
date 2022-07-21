"""
Unit tests for sheet find functions
"""
import re
import unittest
from collections import namedtuple
import gspread

from sheets import find, find_all

from .base import TestBase


Expected = namedtuple("Expected", ['count', 'row', 'col', 'value'])


class TestLoad(TestBase):
    """
    Units tests for sheet find functions
    """

    def test_find(self):
        """
        Test find cell
        """
        worksheet_name = 'find-worksheet'

        sheet = self.add_sheet(worksheet_name)

        # add data
        expected = Expected(1, 2, 2, 'find-me')
        for data in [
            ['not-here', 'nor-here', 'nope'],
            ['not-me', expected.value, 'nor-me']
        ]:
            result = sheet.append_row(data)
            self.assertIsNotNone(result)
            self.assertTrue('updates' in result)
            self.assertEqual(result['updates']['updatedCells'], len(data))

        # check find; none, row & column scopes
        for i in range(3):
            with self.subTest(msg=f'check scope {i}'):
                row = None
                col = None
                if i == 1:
                    row = expected.row # check find with row scope
                elif i == 2:
                    col = expected.col # check find with col scope

                # check find
                cell = find(sheet, expected.value, row=row, col=col)
                self.assert_cell(cell, expected)

        # check find in wrong row
        self.assertGreater(expected.row, 1) # expected positions must be greater than 1
        cell = find(sheet, expected.value, row=expected.row - 1)
        self.assertIsNone(cell)

        # check find in wrong col
        self.assertGreater(expected.col, 1) # expected positions must be greater than 1
        cell = find(sheet, expected.value, col=expected.col - 1)
        self.assertIsNone(cell)

        # tidy up
        self.tidy_up_sheets(
            [ (worksheet_name, sheet) ]
        )


    def assert_cell(self, cell: gspread.cell.Cell, expected: Expected):
        """
        Assert cell info

        Args:
            cell (gspread.cell.Cell): found cell
            expected (Expected): expected info
        """
        self.assertIsNotNone(cell)
        self.assertEqual(cell.value, expected.value)
        self.assertEqual(cell.row, expected.row)
        self.assertEqual(cell.col, expected.col)


    def test_find_all(self):
        """
        Test find cell
        """
        worksheet_name = 'find-all-worksheet'

        sheet = self.add_sheet(worksheet_name)

        # add data
        expected_results = [
            Expected(2, 0, 0, ''),
            Expected(1, 2, 2, 'find-me'),
            Expected(1, 3, 3, 'find-you'),
        ]
        for data in [
            ['not-here', 'nor-here', 'nope'],
            ['not-me', expected_results[1].value, 'nor-me'],
            ['not-me', 'nor-me', expected_results[2].value]
        ]:
            result = sheet.append_row(data)
            self.assertIsNotNone(result)
            self.assertTrue('updates' in result)
            self.assertEqual(result['updates']['updatedCells'], len(data))

        # check find; none, row & column scopes
        pattern = re.compile(r"^find-.+")
        for i in range(3):
            with self.subTest(msg=f'check scope {i}'):
                expect_result = expected_results[i]
                row = None
                col = None
                if i == 1:
                    row = expect_result.row # check find with row scope
                elif i == 2:
                    col = expect_result.col # check find with col scope

                # check find
                cells = find_all(sheet, pattern, row=row, col=col)
                self.assertIsNotNone(cells)
                self.assertEqual(len(cells), expect_result.count)

                if i == 0:
                    for j in range(1, 3):
                        with self.subTest(msg=f'check cell {j}'):
                            self.assert_cell(cells[j - 1], expected_results[j])
                else:
                    self.assert_cell(cells[0], expected_results[i])

        # check find in wrong row
        not_expected = expected_results[1]
        self.assertGreater(not_expected.row, 1) # expected positions must be greater than 1
        cells = find_all(sheet, pattern, row=not_expected.row - 1)
        self.assertEqual(len(cells), 0)

        # # check find in wrong col
        self.assertGreater(not_expected.col, 1) # expected positions must be greater than 1
        cells = find_all(sheet, pattern, col=not_expected.col - 1)
        self.assertEqual(len(cells), 0)

        # tidy up
        self.tidy_up_sheets(
            [ (worksheet_name, sheet) ]
        )


if __name__ == '__main__':
    unittest.main()
