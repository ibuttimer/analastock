"""
Google Sheets search related functions
"""
import re
from typing import List, Union
from gspread.worksheet import Worksheet
from gspread.cell import Cell
from gspread.utils import rowcol_to_a1

from stock import CompanyColumn, Company
from utils import Pagination

from .find_info import find_all
from .save_sheet import companies_sheet


def get_companies(
        ranges: List[str],
        sheet: Worksheet = None,
) -> List[Company]:
    """
    Return companies from ranges list

    Args:
        ranges (List[str]): list of ranges
        sheet (gspread.worksheet.Worksheet, optional):
                worksheet to read. Default to None

    Returns:
        List[Company]
    """
    if not sheet:
        sheet = companies_sheet()

    results = []

    if sheet:
        # https://docs.gspread.org/en/v5.4.0/api/models/worksheet.html#gspread.worksheet.Worksheet.batch_get
        results = [
            # unpack first entry in ValueRange as args for Company
            Company.company_of(*company[0]) \
                for company in sheet.batch_get(ranges)
        ]

    return results

def search_company(
            criteria: str,
            col: CompanyColumn,
            sheet: Worksheet = None,
            page_size: int = 10,
            exact_match: bool = False
        ) -> Union[Pagination, None]:
    """
    Return all companies with values matching the specified criteria.

    Results are return as a Pagination of the sheet ranges with the data,
    and the Pagination::transform_func function retrieves the actual
    company data as required.

    Args:
        criteria (str): company value or part of value to match
        col (CompanyColumn): column to search
        sheet (gspread.worksheet.Worksheet, optional):
                worksheet to read. Default to None
        page_size (int, optional): pagination page size. Defaults to 10.
        exact_match (bool, optional): exact match. Default to False.

    Returns:
        Pagination: paginated results or None of not found
    """
    if not sheet:
        sheet = companies_sheet()

    pagination = None

    if sheet:
        pattern = criteria if exact_match else \
                        re.compile(rf".*{criteria}.*", flags=re.IGNORECASE)
        matches: List[Cell] = find_all(sheet, pattern, col=col.value)

        # The pagination implementation is required as,
        # Worksheet::batch_get passes the ranges as parameters in the url.
        # So for a large number of matches this results in long urls which
        # get truncated.

        if len(matches) > 0:
            # generate ranges for results; columns width to match CompanyColumn
            ranges = [
                f'{rowcol_to_a1(cell.row, 1)}:'\
                f'{rowcol_to_a1(cell.row, len(CompanyColumn))}' \
                    for cell in matches
            ]

            def get_page_companies(ranges: List[str]):
                return get_companies(ranges, sheet=sheet)

            pagination = Pagination(
                ranges, page_size=page_size, transform_func=get_page_companies)

    return pagination
