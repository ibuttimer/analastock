"""
Google Sheets find data related functions
"""
from datetime import datetime, date
from typing import List, Union
import gspread
import pandas as pd

from stock import DfColumn


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


def read_data_by_date(
        sheet: gspread.worksheet.Worksheet,
        min_date: Union[datetime, date],
        max_date: Union[datetime, date],
        sorted_asc: bool = True
) -> pd.DataFrame:
    """
    Read data within the specified date limits

    Args:
        sheet (gspread.worksheet.Worksheet): worksheet to read
        min_date (Union[datetime, date]): min date (inclusive)
        max_date (Union[datetime, date]): max date (inclusive)
        sorted_asc (bool): sorted in ascending order flag; default True

    Returns:
        panda.DataFrame: data frame of data
    """
    if isinstance(min_date, datetime):
        min_date = min_date.date()
    if isinstance(max_date, datetime):
        max_date = max_date.date()

    # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.from_records.html
    # Data can be provided as a list of dicts
    list_of_dicts = [
        {
            title: line[col] for col, title in enumerate(DfColumn.titles())
        } for line in sheet.get_all_values()
    ]
    data_frame = pd.DataFrame(list_of_dicts, columns=DfColumn.titles())

    # everything is a string at the moment, convert appropriately
    for column in DfColumn:
        if column == DfColumn.DATE:
            data_frame[column.title] = pd.to_datetime(data_frame[column.title])
            data_frame[column.title] = data_frame[column.title].dt.date
        else:
            data_frame[column.title] = pd.to_numeric(data_frame[column.title])

    # filter by min & max dates
    date_frame = data_frame[(data_frame[DfColumn.DATE.title] >= min_date) &
                (data_frame[DfColumn.DATE.title] <= max_date)]

    # return data in chronological order
    return date_frame.sort_values(by=DfColumn.DATE.title, ascending=sorted_asc)
