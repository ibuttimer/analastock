"""
Google Sheets search related functions
"""
import re
from typing import List
import gspread

from stock import CompanyColumn, Company
from utils import COMPANIES_SHEET

from .find_info import find_all
from .load_sheet import sheet_exists


def search_company(
        name: str,
        sheet: gspread.worksheet.Worksheet = None
) -> List[Company]:
    """
    Return all companies with names matching specified name

    Args:
        sheet (gspread.worksheet.Worksheet): worksheet to read
        name (str): company name or part of name to match

    Returns:
        List[Company]
    """
    if not sheet:
        sheet = sheet_exists(COMPANIES_SHEET)

    results = []

    if sheet:
        pattern = re.compile(rf".*{name}.*", flags=re.IGNORECASE)
        matches: List[gspread.cell.Cell] = find_all(
            sheet, pattern, col=CompanyColumn.NAME.value)

        # TODO implement pagination of requests for large number of matches
        # they are concatenated are the params for the request url and
        # it gets truncated

        if len(matches) > 0:
            # generate ranges for results; 4 columns wide to match CompanyColumn
            ranges = [
                f'A{cell.row}:D{cell.row}' for cell in matches
            ]
            # https://docs.gspread.org/en/v5.4.0/api/models/worksheet.html#gspread.worksheet.Worksheet.batch_get
            results = [
                # unpack first entry in ValueRange as args for Company
                Company(*company[0]) for company in sheet.batch_get(ranges)
            ]

    return results
