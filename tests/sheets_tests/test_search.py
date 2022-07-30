"""
Unit tests for sheet search functions
"""
from typing import List
import unittest

from sheets import search_company
from stock import Company
from utils import Pagination

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

        # test data for Company 1 - Company 20
        num_companies = 20
        company_name = 'Company'
        test_data = [
            [
                f'EXC{(i // (num_companies / 2)) + 1}', # exchange code
                f'COMP{i + 1}',             # symbol
                f'{company_name} {i + 1} D.A.C',   # name
                'Industrials'               # sector
            ] for i in range(0, num_companies)
        ]

        # add data
        for data in test_data:
            result = sheet.append_row(data)
            self.assertIsNotNone(result)
            self.assertTrue('updates' in result)
            self.assertEqual(result['updates']['updatedCells'], len(data))

        # check find all
        pg_result = search_company(company_name.lower(), sheet=sheet)
        self.assertTrue(isinstance(pg_result, Pagination))

        pg_result.set_page_size(num_companies)
        results = pg_result.get_current_page()

        self.assertEqual(len(test_data), pg_result.num_items)
        self.assertEqual(len(test_data), len(results))
        for i, entry in enumerate(test_data):
            with self.subTest(msg=f'entry[{i}] {entry}'):
                self.assert_company(results[i], entry)

        # check find some
        partial_name = f'{company_name} 1'
        pg_result = search_company(partial_name, sheet=sheet)
        self.assertTrue(isinstance(pg_result, Pagination))

        # expecting Company 1 & Company 10 - Company 19, i.e. 11
        pg_result.set_page_size(num_companies)
        results = pg_result.get_current_page()
        expected_partials = len(
            list(
                filter(
                    lambda entry: entry.name.startswith(partial_name), results
                )
            )
        )

        self.assertEqual(expected_partials, pg_result.num_items)
        self.assertEqual(expected_partials, len(results))
        res_idx = 0
        for i, entry in enumerate(test_data):
            if not entry[0].startswith(partial_name):
                continue

            with self.subTest(msg=f'entry[{i}] {entry}'):
                self.assert_company(results[res_idx], entry)
                res_idx += 1

        # check find none
        pg_result = search_company('DNE', sheet=sheet)
        self.assertTrue(isinstance(pg_result, Pagination))

        pg_result.set_page_size(num_companies)
        results = pg_result.get_current_page()

        self.assertEqual(0, pg_result.num_items)
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
