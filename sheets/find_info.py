"""
Google Sheets find data related functions
"""
from typing import List, Union
import gspread


def find(
        sheet: gspread.worksheet.Worksheet,
        query: Union[str, object], row: int = None, col: int = None,
        case_sensitive: bool = True
    ) -> Union[gspread.cell.Cell, None]:
    """
    Find the first cell matching the query.

    Args:
        sheet (gspread.worksheet.Worksheet): worksheet to search
        query (Union[str, Regular Expression Object]): A literal string to match or
                                            compiled regular expression
        row (int, optional): One-based row number to scope the search.
                                Defaults to None.
        col (int, optional): One-based column number to scope the search.
                                Defaults to None.
        case_sensitive (bool, optional): comparison is case sensitive if True, 
                                case insensitive otherwise. Defaults to True.
                                Does not apply to regular expressions.

    Returns:
        Union[gspread.cell.Cell, None]: cell
    """
    # https://docs.gspread.org/en/v5.4.0/api/models/worksheet.html#gspread.worksheet.Worksheet.find

    return sheet.find(query, in_row=row, in_column=col, case_sensitive=case_sensitive)


def find_all(
        sheet: gspread.worksheet.Worksheet,
        query: Union[str, object], row: int = None, col: int = None,
        case_sensitive: bool = True
    ) -> List[gspread.cell.Cell]:
    """
    Find all cells matching the query.

    Args:
        sheet (gspread.worksheet.Worksheet): worksheet to search
        query (Union[str, re.RegexObject]): A literal string to match or
                                            compiled regular expression
        row (int, optional): One-based row number to scope the search.
                                Defaults to None.
        col (int, optional): One-based column number to scope the search.
                                Defaults to None.
        case_sensitive (bool, optional): comparison is case sensitive if True,
                                case insensitive otherwise. Defaults to True.
                                Does not apply to regular expressions.

    Returns:
        List[gspread.cell.Cell]: list of cells
    """

    # https://docs.gspread.org/en/v5.4.0/api/models/worksheet.html#gspread.worksheet.Worksheet.findall

    return sheet.findall(query, in_row=row, in_column=col, case_sensitive=case_sensitive)
