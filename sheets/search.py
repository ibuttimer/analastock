"""
Google Sheets search related functions
"""
import re
from typing import List, Union
from gspread.worksheet import Worksheet
from gspread.cell import Cell

from stock import CompanyColumn, Company
from utils import Pagination

from .find_info import find_all
from .load_sheet import (
    companies_sheet, eft_sheet, mutual_sheet, future_sheet, index_sheet
)
from .utils import cells_range


DEFAULT_PAGE_SIZE = 10


def get_entities(
        ranges: List[str],
        sheet: Worksheet
) -> List[Company]:
    """
    Return entities from ranges list

    Args:
        ranges (List[str]): list of ranges
        sheet (gspread.worksheet.Worksheet): worksheet to read

    Returns:
        List[Company]
    """
    results = []

    if sheet:
        # https://docs.gspread.org/en/v5.4.0/api/models/worksheet.html#gspread.worksheet.Worksheet.batch_get
        results = [
            # unpack first entry in ValueRange as args for Company
            Company.company_of(*company[0]) \
                for company in sheet.batch_get(ranges)
        ]

    return results


def search_meta(
            criteria: str,
            col: CompanyColumn,
            sheet: Worksheet,
            page_size: int = DEFAULT_PAGE_SIZE,
            exact_match: bool = False
        ) -> Union[Pagination, None]:
    """
    Return all entities with values matching the specified criteria.

    Results are return as a Pagination of the sheet ranges with the data,
    and the Pagination::transform_func function retrieves the actual
    data as required.

    Args:
        criteria (str): value or part of value to match
        col (CompanyColumn): column to search
        sheet (gspread.worksheet.Worksheet): worksheet to read
        page_size (int, optional): pagination page size. Defaults to 10.
        exact_match (bool, optional): exact match. Default to False.

    Returns:
        Pagination: paginated results or None of not found
    """
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
            # e.g. 'A1:E1'
            # Note: rows/cols are 1-based
            ranges = [
                cells_range(cell.row, 1, cell.row, len(CompanyColumn)) \
                    for cell in matches
            ]

            def get_page(ranges: List[str]):
                return get_entities(ranges, sheet)

            pagination = Pagination(
                ranges, page_size=page_size, transform_func=get_page)

    return pagination


def search_company(
            criteria: str,
            col: CompanyColumn,
            sheet: Worksheet = None,
            page_size: int = DEFAULT_PAGE_SIZE,
            exact_match: bool = False
        ) -> Union[Pagination, None]:
    """
    Return all companies with values matching the specified criteria.

    Results are return as a Pagination of the sheet ranges with the data,
    and the Pagination::transform_func function retrieves the actual
    data as required.

    Args:
        criteria (str): value or part of value to match
        col (CompanyColumn): column to search
        sheet (gspread.worksheet.Worksheet, optional):
                worksheet to read. Default to None
        page_size (int, optional): pagination page size. Defaults to 10.
        exact_match (bool, optional): exact match. Default to False.

    Returns:
        Pagination: paginated results or None of not found
    """
    return search_meta(
            criteria, col, sheet if sheet else companies_sheet(),
            page_size=page_size, exact_match=exact_match)

def search_eft(
            criteria: str,
            col: CompanyColumn,
            sheet: Worksheet = None,
            page_size: int = DEFAULT_PAGE_SIZE,
            exact_match: bool = False
        ) -> Union[Pagination, None]:
    """
    Return all EFT with values matching the specified criteria.

    Results are return as a Pagination of the sheet ranges with the data,
    and the Pagination::transform_func function retrieves the actual
    data as required.

    Args:
        criteria (str): value or part of value to match
        col (CompanyColumn): column to search
        sheet (gspread.worksheet.Worksheet, optional):
                worksheet to read. Default to None
        page_size (int, optional): pagination page size. Defaults to 10.
        exact_match (bool, optional): exact match. Default to False.

    Returns:
        Pagination: paginated results or None of not found
    """
    return search_meta(
            criteria, col, sheet if sheet else eft_sheet(),
            page_size=page_size, exact_match=exact_match)


def search_mutual(
            criteria: str,
            col: CompanyColumn,
            sheet: Worksheet = None,
            page_size: int = DEFAULT_PAGE_SIZE,
            exact_match: bool = False
        ) -> Union[Pagination, None]:
    """
    Return all Mutual Funds with values matching the specified criteria.

    Results are return as a Pagination of the sheet ranges with the data,
    and the Pagination::transform_func function retrieves the actual
    data as required.

    Args:
        criteria (str): value or part of value to match
        col (CompanyColumn): column to search
        sheet (gspread.worksheet.Worksheet, optional):
                worksheet to read. Default to None
        page_size (int, optional): pagination page size. Defaults to 10.
        exact_match (bool, optional): exact match. Default to False.

    Returns:
        Pagination: paginated results or None of not found
    """
    return search_meta(
            criteria, col, sheet if sheet else mutual_sheet(),
            page_size=page_size, exact_match=exact_match)


def search_future(
            criteria: str,
            col: CompanyColumn,
            sheet: Worksheet = None,
            page_size: int = DEFAULT_PAGE_SIZE,
            exact_match: bool = False
        ) -> Union[Pagination, None]:
    """
    Return all Futures with values matching the specified criteria.

    Results are return as a Pagination of the sheet ranges with the data,
    and the Pagination::transform_func function retrieves the actual
    data as required.

    Args:
        criteria (str): value or part of value to match
        col (CompanyColumn): column to search
        sheet (gspread.worksheet.Worksheet, optional):
                worksheet to read. Default to None
        page_size (int, optional): pagination page size. Defaults to 10.
        exact_match (bool, optional): exact match. Default to False.

    Returns:
        Pagination: paginated results or None of not found
    """
    return search_meta(
            criteria, col, sheet if sheet else future_sheet(),
            page_size=page_size, exact_match=exact_match)


def search_index(
            criteria: str,
            col: CompanyColumn,
            sheet: Worksheet = None,
            page_size: int = DEFAULT_PAGE_SIZE,
            exact_match: bool = False
        ) -> Union[Pagination, None]:
    """
    Return all Indices with values matching the specified criteria.

    Results are return as a Pagination of the sheet ranges with the data,
    and the Pagination::transform_func function retrieves the actual
    data as required.

    Args:
        criteria (str): value or part of value to match
        col (CompanyColumn): column to search
        sheet (gspread.worksheet.Worksheet, optional):
                worksheet to read. Default to None
        page_size (int, optional): pagination page size. Defaults to 10.
        exact_match (bool, optional): exact match. Default to False.

    Returns:
        Pagination: paginated results or None of not found
    """
    return search_meta(
            criteria, col, sheet if sheet else index_sheet(),
            page_size=page_size, exact_match=exact_match)


def search_all(
            criteria: str,
            col: CompanyColumn,
            page_size: int = DEFAULT_PAGE_SIZE,
            exact_match: bool = False
        ) -> Union[Pagination, None]:
    """
    Return all entities with values matching the specified criteria.

    Results are return as a Pagination of the sheet ranges with the data,
    and the Pagination::transform_func function retrieves the actual
    data as required.

    Args:
        criteria (str): value or part of value to match
        col (CompanyColumn): column to search
        page_size (int, optional): pagination page size. Defaults to 10.
        exact_match (bool, optional): exact match. Default to False.

    Returns:
        Pagination: paginated results or None of not found
    """
    pagination = None

    for func in [
            search_company, search_eft, search_mutual, search_future,
            search_index]:
        pagination = func(
            criteria, col, page_size=page_size, exact_match=exact_match)
        if pagination is not None:
            break

    return pagination
