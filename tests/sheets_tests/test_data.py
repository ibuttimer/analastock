"""
Unit tests for sheet data functions
"""
from datetime import date, timedelta
from typing import List
import unittest
from collections import namedtuple
import gspread

from sheets import read_data_by_date, check_partial
from stock import StockParam

from .base import TestBase
from .sheet_utils import (
    add_month, add_sheet_data, JAN, FEB, MAR, APR, JUN, JUL, AUG, SEP, NOV
)

Gap = namedtuple("Gap", ['date', 'months'])


class TestData(TestBase):
    """
    Units tests for sheet data functions
    """

    def test_read_data_gaps_same_year(self):
        """
        Test read data gaps
        """
        worksheet_name = 'data-gaps-worksheet'

        sheet = self.add_sheet(worksheet_name, del_if_exists=True)

        stock_param = StockParam.stock_param_of(
            "x", date(2022, JAN, 1), date(2022, JUL, 1))

        expected_gaps = add_data_with_gaps(sheet, stock_param, [
            Gap(date(2022, FEB, 1), 1),
            Gap(date(2022, APR, 1), 2)
        ])

        TestData.check_gaps(self, sheet, stock_param, expected_gaps)

        # tidy up
        self.tidy_up_sheets(
            [ (worksheet_name, sheet) ]
        )

    def test_read_data_gaps_start_end_gaps(self):
        """
        Test read data gaps
        """
        worksheet_name = 'data-gaps-start-end-worksheet'

        sheet = self.add_sheet(worksheet_name, del_if_exists=True)

        stock_param = StockParam.stock_param_of(
            "x", date(2022, JAN, 1), date(2022, JUL, 1))

        expected_gaps = add_data_with_gaps(sheet, stock_param, [
            Gap(date(2022, JAN, 1), 1),
            Gap(date(2022, JUN, 1), 1)
        ])

        TestData.check_gaps(self, sheet, stock_param, expected_gaps)

        # tidy up
        self.tidy_up_sheets(
            [ (worksheet_name, sheet) ]
        )


    def test_read_data_gaps_multi_year(self):
        """
        Test read data gaps
        """
        worksheet_name = 'data-gaps-multi-worksheet'

        sheet = self.add_sheet(worksheet_name, del_if_exists=True)

        stock_param = StockParam.stock_param_of(
            "x", date(2021, AUG, 1), date(2022, JUL, 1))

        expected_gaps = add_data_with_gaps(sheet, stock_param, [
            Gap(date(2021, SEP, 1), 1),
            Gap(date(2021, NOV, 1), 3),
            Gap(date(2022, MAR, 1), 1)
        ])

        TestData.check_gaps(self, sheet, stock_param, expected_gaps)

        # tidy up
        self.tidy_up_sheets(
            [ (worksheet_name, sheet) ]
        )

    @staticmethod
    def check_gaps(
            instance,
            sheet: gspread.worksheet.Worksheet, 
            stock_param: StockParam, 
            expected_gaps: List[StockParam]
        ):
        """
        Check gaps test

        Args:
            instance (_type_): _description_
            sheet (gspread.worksheet.Worksheet): _description_
            stock_param (StockParam): _description_
            expected_gaps (List[StockParam]): _description_
        """
        # get data from sheet
        data_frame = read_data_by_date(
            sheet, stock_param.from_date, stock_param.to_date
        )

        gaps = check_partial(data_frame, stock_param)

        instance.assertEqual(len(gaps), len(expected_gaps))
        instance.assertListEqual(gaps, expected_gaps)



def add_data_with_gaps(
        sheet: gspread.worksheet.Worksheet,
        stock_param: StockParam,
        gap_month: List[Gap]
    ) -> List[StockParam]:
    """
    Add data with gaps

    Args:
        sheet (gspread.worksheet.Worksheet): worksheet to add to
        stock_param (StockParam): params for whole data set
        gap_month (List[Gap]): list of gaps to add

    Returns:
        List[StockParam]: list of params for gaps
    """
    # TODO add this functionality to add_sheet_data

    expected_gaps: List[StockParam] = []
    gap_index = 0
    skip_months = 0

    # add data, one month at at time with gaps
    start_date = stock_param.from_date
    end_date = stock_param.to_date
    for year in range(start_date.year, end_date.year + 1):

        if start_date.year == end_date.year:
            # same year
            start_month = start_date.month
            end_month = end_date.month
        else:
            # multiple years
            start_month = 1 if year > start_date.year else start_date.month
            end_month = 12 if year < end_date.year else end_date.month

        for month in range(start_month, end_month + 1):
            mth_start = date(year, month, 1)
            next_mth = add_month(mth_start)

            gap = gap_month[gap_index] if gap_index < len(gap_month) else None

            if gap and year == gap.date.year and month == gap.date.month:
                # add gap
                expected_gaps.append(
                    StockParam.stock_param_of(
                        stock_param.symbol,
                        mth_start, add_month(mth_start, gap.months)
                    )
                )
                skip_months = gap.months - 1
                if not skip_months:
                    gap_index += 1  # index of next gap to look for

            elif skip_months:
                # skip gap months
                skip_months -= 1
                if not skip_months:
                    gap_index += 1  # index of next gap to look for
            else:
                add_sheet_data(sheet, mth_start, next_mth - timedelta(days=1))

    return expected_gaps


if __name__ == '__main__':
    unittest.main()
