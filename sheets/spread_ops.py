"""
Wrapper functions for gspread functions
"""
from typing import Any

import gspread
import google.auth.exceptions
from utils import error, read_manager, write_manager
from .client import gspread_client

SHEETS_ERR_MSG = 'Google Sheets error, functionality unavailable\n' \
                 'Please check the network connection'


def sheet_find(sheet: gspread.worksheet.Worksheet,
               query, in_row=None, in_column=None, case_sensitive=True):
    """
    Finds the first cell matching the query.

    Args:
        sheet (gspread.worksheet.Worksheet): worksheet to search

    For other details see
        https://docs.gspread.org/en/v5.4.0/api/models/worksheet.html#gspread.worksheet.Worksheet.find
    """
    def operation_func() -> Any:
        return sheet.find(
            query, in_row=in_row, in_column=in_column,
            case_sensitive=case_sensitive)

    read_manager().acquire()
    try:
        result = read_manager().perform(operation_func)
    finally:
        read_manager().release()

    return result


def sheet_findall(sheet: gspread.worksheet.Worksheet,
                  query, in_row=None, in_column=None, case_sensitive=True):
    """
    Finds all cells matching the query.

    Args:
        sheet (gspread.worksheet.Worksheet): worksheet to search

    For other details see
        https://docs.gspread.org/en/v5.4.0/api/models/worksheet.html#gspread.worksheet.Worksheet.findall
    """
    def operation_func() -> Any:
        return sheet.findall(
            query, in_row=in_row, in_column=in_column,
            case_sensitive=case_sensitive)

    read_manager().acquire()
    try:
        result = read_manager().perform(operation_func)
    finally:
        read_manager().release()

    return result


def sheet_get_values(sheet: gspread.worksheet.Worksheet,
                     range_name=None, **kwargs):
    """
    Returns a list of lists containing all values from specified range.

    Args:
        sheet (gspread.worksheet.Worksheet): worksheet to search

    For other details see
        https://docs.gspread.org/en/v5.4.0/api/models/worksheet.html#gspread.worksheet.Worksheet.get_values
    """
    def operation_func() -> Any:
        return sheet.get_values(range_name, **kwargs)

    read_manager().acquire()
    try:
        result = read_manager().perform(operation_func)
    finally:
        read_manager().release()

    return result


def sheet_append_row(
        sheet: gspread.worksheet.Worksheet,
        values,
        value_input_option=gspread.utils.ValueInputOption.raw,
        insert_data_option=None,
        table_range=None,
        include_values_in_response=False,
):
    """
    Adds a row to the worksheet and populates it with values.

    Args:
        sheet (gspread.worksheet.Worksheet): worksheet to update

    For other details see
        https://docs.gspread.org/en/v5.4.0/api/models/worksheet.html#gspread.worksheet.Worksheet.append_row
    """
    def operation_func() -> Any:
        return sheet.append_row(
            values, value_input_option=value_input_option,
            insert_data_option=insert_data_option, table_range=table_range,
            include_values_in_response=include_values_in_response)

    write_manager().acquire()
    try:
        result = write_manager().perform(operation_func)
    finally:
        write_manager().release()

    return result


def sheet_append_rows(
        sheet: gspread.worksheet.Worksheet,
        values,
        value_input_option=gspread.utils.ValueInputOption.raw,
        insert_data_option=None,
        table_range=None,
        include_values_in_response=False,
):
    """
    Adds multiple rows to the worksheet and populates them with values.

    Args:
        sheet (gspread.worksheet.Worksheet): worksheet to update

    For other details see
        https://docs.gspread.org/en/v5.4.0/api/models/worksheet.html#gspread.worksheet.Worksheet.append_rows
    """
    def operation_func() -> Any:
        return sheet.append_rows(
            values, value_input_option=value_input_option,
            insert_data_option=insert_data_option, table_range=table_range,
            include_values_in_response=include_values_in_response)

    write_manager().acquire()
    try:
        result = write_manager().perform(operation_func)
    finally:
        write_manager().release()

    return result


def sheet_batch_update(sheet: gspread.worksheet.Worksheet, data, **kwargs):
    """
    Sets values in one or more cell ranges of the sheet at once.

    Args:
        sheet (gspread.worksheet.Worksheet): worksheet to update

    For other details see
        https://docs.gspread.org/en/v5.4.0/api/models/worksheet.html#gspread.worksheet.Worksheet.batch_update
    """
    def operation_func() -> Any:
        return sheet.batch_update(data, **kwargs)

    write_manager().acquire()
    try:
        result = write_manager().perform(operation_func)
    finally:
        write_manager().release()

    return result


def sheet_clear(sheet: gspread.worksheet.Worksheet):
    """
    Clears all cells in the worksheet.

    Args:
        sheet (gspread.worksheet.Worksheet): worksheet to update

    For other details see
        https://docs.gspread.org/en/v5.4.0/api/models/worksheet.html#gspread.worksheet.Worksheet.clear
    """
    def operation_func() -> Any:
        return sheet.clear()

    write_manager().acquire()
    try:
        result = write_manager().perform(operation_func)
    finally:
        write_manager().release()

    return result


def sheet_batch_format(sheet: gspread.worksheet.Worksheet, formats):
    """
    Formats cells in batch.

    Args:
        sheet (gspread.worksheet.Worksheet): worksheet to update

    For other details see
        https://docs.gspread.org/en/v5.4.0/api/models/worksheet.html#gspread.worksheet.Worksheet.batch_format
    """
    def operation_func() -> Any:
        return sheet.batch_format(formats)

    write_manager().acquire()
    try:
        result = write_manager().perform(operation_func)
    finally:
        write_manager().release()

    return result


def sheet_batch_get(sheet: gspread.worksheet.Worksheet, ranges, **kwargs):
    """
    Returns one or more ranges of values from the sheet.

    Args:
        sheet (gspread.worksheet.Worksheet): worksheet to update

    For other details see
        https://docs.gspread.org/en/v5.4.0/api/models/worksheet.html#gspread.worksheet.Worksheet.batch_get
    """
    def operation_func() -> Any:
        return sheet.batch_get(ranges, **kwargs)

    read_manager().acquire()
    try:
        result = read_manager().perform(operation_func)
    finally:
        read_manager().release()

    return result


def spreadsheet_worksheets(spreadsheet: gspread.spreadsheet.Spreadsheet):
    """
    Returns a list of all :class:`worksheets <gspread.worksheet.Worksheet>`
    in a spreadsheet.

    Args:
        spreadsheet: (gspread.spreadsheet.Spreadsheet):
                spreadsheet to get worksheets from

    For other details see
        https://docs.gspread.org/en/v5.4.0/api/models/spreadsheet.html#gspread.spreadsheet.Spreadsheet.worksheets
    """
    def operation_func() -> Any:
        return spreadsheet.worksheets()

    read_manager().acquire()
    try:
        result = read_manager().perform(operation_func)
    finally:
        read_manager().release()

    return result


def spreadsheet_add_worksheet(spreadsheet: gspread.spreadsheet.Spreadsheet,
                              title, rows, cols, index=None):
    """
    Adds a new worksheet to a spreadsheet.

    Args:
        spreadsheet: (gspread.spreadsheet.Spreadsheet):
                spreadsheet to add worksheet to

    For other details see
        https://docs.gspread.org/en/v5.4.0/api/models/spreadsheet.html#gspread.spreadsheet.Spreadsheet.add_worksheet
    """
    def operation_func() -> Any:
        return spreadsheet.add_worksheet(title, rows, cols, index=index)

    write_manager().acquire()
    try:
        result = write_manager().perform(operation_func)
    finally:
        write_manager().release()

    return result


def spreadsheet_del_worksheet(
        spreadsheet: gspread.spreadsheet.Spreadsheet, worksheet):
    """
    Deletes a worksheet from a spreadsheet.

    Args:
        spreadsheet: (gspread.spreadsheet.Spreadsheet):
                spreadsheet to add worksheet to

    For other details see
        https://docs.gspread.org/en/v5.4.0/api/models/spreadsheet.html#gspread.spreadsheet.Spreadsheet.del_worksheet
    """
    def operation_func() -> Any:
        return spreadsheet.del_worksheet(worksheet)

    write_manager().acquire()
    try:
        result = write_manager().perform(operation_func)
    finally:
        write_manager().release()

    return result


def client_open_spreadsheet(name: str) -> gspread.spreadsheet.Spreadsheet:
    """
    Open a spreadsheet

    Args:
        name (str): name of spreadsheet

    Raises:
        ValueError: if spreadsheet not found

    Returns:
        gspread.spreadsheet.Spreadsheet: spreadsheet
    """
    spreadsheet = None

    def operation_func() -> Any:
        return gspread_client().open(name)

    read_manager().acquire()
    try:
        spreadsheet = read_manager().perform(operation_func)
    except gspread.exceptions.SpreadsheetNotFound as exc:
        raise ValueError(f"Spreadsheet {name} not found") from exc
    except google.auth.exceptions.GoogleAuthError:
        error(SHEETS_ERR_MSG)
    finally:
        read_manager().release()

    return spreadsheet
