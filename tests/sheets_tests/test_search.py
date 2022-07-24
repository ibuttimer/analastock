"""
Unit tests for sheet search functions
"""
from typing import List
import unittest

from sheets import search_company
from stock import Company

from .base import TestBase


class TestSearch(TestBase):
    """
    Units tests for sheet search functions
    """

    def test_search(self):
        """
        Test search company
        """
        worksheet_name = 'find-company'

        sheet = self.add_sheet(worksheet_name, del_if_exists=True)

        # test data for COMP1-COMP20
        comp_symbol = 'COMP'
        test_data = [
            [
                f'EXC{(i // 10) + 1}',      # exchange code
                f'{comp_symbol}{i + 1}',    # symbol
                f'Company {i + 1} D.A.C',   # name
                'Industrials'               # sector
            ] for i in range(0, 20)
        ]

        # add data
        for data in test_data:
            result = sheet.append_row(data)
            self.assertIsNotNone(result)
            self.assertTrue('updates' in result)
            self.assertEqual(result['updates']['updatedCells'], len(data))

        # check find all
        results = search_company(sheet, comp_symbol.lower())
        self.assertEqual(len(test_data), len(results))
        for i, entry in enumerate(test_data):
            with self.subTest(msg=f'entry[{i}] {entry}'):
                self.assert_company(results[i], entry)

        # check find some
        partial_name = f'{comp_symbol}1'
        results = search_company(sheet, partial_name)
        # expecting COMP1 & COMP10-COMP19, i.e. 11
        self.assertEqual(11, len(results))
        res_idx = 0
        for i, entry in enumerate(test_data):
            if not entry[0].startswith(partial_name):
                continue

            with self.subTest(msg=f'entry[{i}] {entry}'):
                self.assert_company(results[res_idx], entry)
                res_idx += 1

        # check find none
        results = search_company(sheet, 'DNE')
        self.assertEqual(0, len(results))

        # tidy up
        self.tidy_up_sheets(
            [ (worksheet_name, sheet) ]
        )


    def assert_company(self, company: Company, expected: List[str]):
        """
        Assert company info

        Args:
            company (Company): found company
            expected (Expected): expected info
        """
        self.assertIsNotNone(company)
        self.assertEqual(company.code, expected[0])
        self.assertEqual(company.symbol, expected[1])
        self.assertEqual(company.name, expected[2])
        self.assertEqual(company.sector, expected[3])


if __name__ == '__main__':
    unittest.main()
