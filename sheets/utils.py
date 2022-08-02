"""
Utility functions for sheets
"""
from typing import List
import gspread
from gspread.utils import rowcol_to_a1


def updated_range(result: dict, inc_sheet_name: bool = False):
    """
    Get the updated range from a gspread result

    Args:
        result (dict): gspread result
        inc_sheet_name (bool, optional): include sheet name flag.
                                        Defaults to False.

    Returns:
        str: updated range
    """
    updated = result['updates']['updatedRange']
    return updated if inc_sheet_name else updated.split('!')[1]


def updated_rows(result: dict):
    """
    Get the number of updated rows from a gspread result

    Args:
        result (dict): gspread result

    Returns:
        str: updated rows
    """
    return result['updates']['updatedRows']


def cell_values(cells: List[gspread.cell.Cell]) -> List[str]:
    """
    Convert a list of cells to a list of values

    Args:
        cells (List[gspread.cell.Cell]): cells list

    Returns:
        List[str]: values list
    """
    return [cell.value for cell in cells]


def cells_range(
        row_top: int, col_left: int, row_bottom: int, col_right: int) -> str:
    """
    Generate a cell range in A1 format

    Args:
        row_top (int): top row (1-based)
        col_left (int): left column (1-based)
        row_bottom (int): bottom row (1-based)
        col_right (int): right column (1-based)

    Returns:
        str: range
    """
    return f'{rowcol_to_a1(row_top, col_left)}:'\
                f'{rowcol_to_a1(row_bottom, col_right)}'