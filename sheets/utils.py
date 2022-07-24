"""
Utility functions for sheets
"""


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
