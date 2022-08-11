"""
Unit tests for sheet find functions
"""
from datetime import date, datetime
import re
import unittest
from collections import namedtuple
import gspread

from sheets import find, find_all, read_data_by_date
from sheets.spread_ops import sheet_append_row
from stock import DfColumn, round_price
from utils import last_day_of_month

from .base import TestBase
from .sheet_utils import (
    add_sheet_data, open_value, high_value, low_value, close_value,
    adj_close_value, volume_value
)


Expected = namedtuple("Expected", ['count', 'row', 'col', 'value'])


class TestFind(TestBase):
    """
    Units tests for sheet find functions
    """

    def test_find(self):
        """
        Test find cell
        """
        worksheet_name = 'find-worksheet'

        sheet = self.add_sheet(worksheet_name, del_if_exists=True)

        # add data
        expected = Expected(1, 2, 2, 'find-me')
        for data in [
            ['not-here', 'nor-here', 'nope'],
            ['not-me', expected.value, 'nor-me']
        ]:
            result = sheet_append_row(sheet, data)
            self.assertIsNotNone(result)
            self.assertTrue('updates' in result)
            self.assertEqual(result['updates']['updatedCells'], len(data))

        # check find; none, row & column scopes
        for i in range(3):
            with self.subTest(msg=f'check scope {i}'):
                row = None
                col = None
                if i == 1:
                    row = expected.row  # check find with row scope
                elif i == 2:
                    col = expected.col  # check find with col scope

                # check find
                cell = find(sheet, expected.value, row=row, col=col)
                self.assert_cell(cell, expected)

        # check find in wrong row
        # expected positions must be greater than 1
        self.assertGreater(expected.row, 1)
        cell = find(sheet, expected.value, row=expected.row - 1)
        self.assertIsNone(cell)

        # check find in wrong col
        # expected positions must be greater than 1
        self.assertGreater(expected.col, 1)
        cell = find(sheet, expected.value, col=expected.col - 1)
        self.assertIsNone(cell)

        # tidy up
        self.tidy_up_sheets(
            [(worksheet_name, sheet)]
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
        Test find cells
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
            result = sheet_append_row(sheet, data)
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
                    row = expect_result.row   # check find with row scope
                elif i == 2:
                    col = expect_result.col   # check find with col scope

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
        # expected positions must be greater than 1
        self.assertGreater(not_expected.row, 1)
        cells = find_all(sheet, pattern, row=not_expected.row - 1)
        self.assertEqual(len(cells), 0)

        # # check find in wrong col
        # expected positions must be greater than 1
        self.assertGreater(not_expected.col, 1)
        cells = find_all(sheet, pattern, col=not_expected.col - 1)
        self.assertEqual(len(cells), 0)

        # tidy up
        self.tidy_up_sheets(
            [(worksheet_name, sheet)]
        )

    def test_read_by_date(self):
        """
        Test read data by date
        """
        worksheet_name = 'read-by-date-worksheet'

        sheet = self.add_sheet(worksheet_name, del_if_exists=True)

        # add data
        jan, feb, mar, apr = (1, 2, 3, 4)
        add_sheet_data(sheet, date(2022, jan, 1), date(2022, apr, 1))

        test_min = datetime(year=2022, month=feb, day=5).date()
        test_max = datetime(year=2022, month=mar, day=5).date()  # exclusive
        data_frame = read_data_by_date(sheet, test_min, test_max)

        row = 0
        for month in range(feb, mar + 1):   # feb - mar
            for day in range(1, last_day_of_month(2022, month) + 1):
                test_date = datetime(year=2022, month=month, day=day).date()
                if test_date < test_min:
                    continue
                if test_date >= test_max:
                    break

                with self.subTest(msg=f'check date {test_date.isoformat()}'):
                    self.assertEqual(
                        data_frame[DfColumn.DATE.title].iat[row], test_date)
                    self.assertEqual(
                        data_frame[DfColumn.OPEN.title].iat[row], round_price(
                            open_value(month, day))
                        )
                    self.assertEqual(
                        data_frame[DfColumn.HIGH.title].iat[row], round_price(
                            high_value(month, day))
                        )
                    self.assertEqual(
                        data_frame[DfColumn.LOW.title].iat[row],
                        round_price(
                            low_value(month, day))
                        )
                    self.assertEqual(
                        data_frame[DfColumn.CLOSE.title].iat[row],
                        round_price(
                            close_value(month, day))
                        )
                    self.assertEqual(
                        data_frame[DfColumn.ADJ_CLOSE.title].iat[row],
                        round_price(
                            adj_close_value(month, day))
                        )
                    self.assertEqual(
                        data_frame[DfColumn.VOLUME.title].iat[row],
                        volume_value(month, day)
                    )

                row += 1

        # tidy up
        self.tidy_up_sheets(
            [(worksheet_name, sheet)]
        )


if __name__ == '__main__':
    unittest.main()
