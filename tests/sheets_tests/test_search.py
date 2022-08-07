"""
Unit tests for sheet search functions
"""
from typing import List
import unittest

from sheets import search_company
from sheets.spread_ops import sheet_append_row
from stock import Company, CompanyColumn
from utils import Pagination

from .base import TestBase


class TestSearch(TestBase):
    """
    Units tests for sheet search functions
    """

    def test_name_search(self):
        """
        Test search company by name
        """
        worksheet_name = 'find-company-name'
        num_companies = 20

        sheet, company_name, _, test_data = \
            self.add_companies(worksheet_name, num_companies)

        # check find all
        pg_result = search_company(
                        company_name.lower(), CompanyColumn.NAME, sheet=sheet)
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
        pg_result = search_company(
                        partial_name, CompanyColumn.NAME, sheet=sheet)
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
            if not entry[CompanyColumn.NAME.value - 1]\
                        .startswith(partial_name):
                continue

            with self.subTest(msg=f'entry[{i}] {entry}'):
                self.assert_company(results[res_idx], entry)
                res_idx += 1

        # check find none
        pg_result = search_company(
                        'DNE', CompanyColumn.NAME, sheet=sheet)
        self.assertIsNone(pg_result)

        # tidy up
        self.tidy_up_sheets(
            [ (worksheet_name, sheet) ]
        )


    def test_symbol_search(self):
        """
        Test search company by symbol
        """
        worksheet_name = 'find-company-symbol'
        num_companies = 20

        sheet, _, company_symbol, test_data = \
            self.add_companies(worksheet_name, num_companies)

        # check find all
        pg_result = search_company(
                    company_symbol.lower(), CompanyColumn.SYMBOL, sheet=sheet)
        self.assertTrue(isinstance(pg_result, Pagination))

        pg_result.set_page_size(num_companies)
        results = pg_result.get_current_page()

        self.assertEqual(len(test_data), pg_result.num_items)
        self.assertEqual(len(test_data), len(results))
        for i, entry in enumerate(test_data):
            with self.subTest(msg=f'entry[{i}] {entry}'):
                self.assert_company(results[i], entry)

        # check find some
        partial_name = f'{company_symbol}1'
        pg_result = search_company(
                        partial_name, CompanyColumn.SYMBOL, sheet=sheet)
        self.assertTrue(isinstance(pg_result, Pagination))

        # expecting COMP1 & COMP10 - COMP19, i.e. 11
        pg_result.set_page_size(num_companies)
        results = pg_result.get_current_page()
        expected_partials = len(
            list(
                filter(
                    lambda entry: \
                        entry.symbol.startswith(partial_name), results
                )
            )
        )

        self.assertEqual(expected_partials, pg_result.num_items)
        self.assertEqual(expected_partials, len(results))
        res_idx = 0
        for i, entry in enumerate(test_data):
            if not entry[CompanyColumn.SYMBOL.value - 1]\
                            .startswith(partial_name):
                continue

            with self.subTest(msg=f'entry[{i}] {entry}'):
                self.assert_company(results[res_idx], entry)
                res_idx += 1

        # check find one exact match
        expected_match = test_data[int(len(test_data) / 2)]
        pg_result = search_company(
                        expected_match[CompanyColumn.SYMBOL.value - 1],
                        CompanyColumn.SYMBOL, sheet=sheet, exact_match=True)
        self.assertTrue(isinstance(pg_result, Pagination))

        pg_result.set_page_size(num_companies)
        results = pg_result.get_current_page()

        self.assertEqual(1, pg_result.num_items)
        self.assertEqual(1, len(results))
        self.assert_company(results[0], expected_match)

        # check find none
        pg_result = search_company(
                        'DNE', CompanyColumn.SYMBOL, sheet=sheet)
        self.assertIsNone(pg_result)

        # tidy up
        self.tidy_up_sheets(
            [ (worksheet_name, sheet) ]
        )


    def add_companies(self, worksheet_name: str, num_companies: int):
        """
        Test search company by symbol
        """
        sheet = self.add_sheet(worksheet_name, del_if_exists=True)

        # test data for Company 1 - Company 20
        company_name = 'Company'
        company_symbol = 'COMP'
        test_data = [
            [
                # following CompanyColumn order
                f'EXC{(i // (num_companies / 2)) + 1}', # exchange code
                f'{company_symbol}{i + 1}',             # symbol
                f'{company_name} {i + 1} D.A.C',   # name
                'Industrials'               # sector
            ] for i in range(0, num_companies)
        ]

        # add data
        for data in test_data:
            result = sheet_append_row(sheet, data)
            self.assertIsNotNone(result)
            self.assertTrue('updates' in result)
            self.assertEqual(result['updates']['updatedCells'], len(data))

        return sheet, company_name, company_symbol, test_data


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
