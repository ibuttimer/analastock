"""
Processing results display functions
"""

from typing import List
from stock import DfStat, DfColumn, CompanyColumn, download_meta_data
from sheets import search_company, save_stock_meta_data
from utils import MAX_LINE_LEN, convert_date_time, DateFormat, drill_dict
from .grid import DGrid, DCell, DRow, FORMAT_WIDTH_MARK, Marker


# 80 Columns
# 12345678901234567890123456789012345678901234567890123456789012345678901234567890

#                                                                         Currency
# Stock : IBM - International Business Machines Corporation                    USD
# Period: 01 Mar 2022* - 01 Jul 2022**
#               Min          Max          Avg         Change         %
# Open      ............ ............ ............ ............ ............
# Low       ............ ............ ............ ............ ............
# High      ............ ............ ............ ............ ............
# Close     ............ ............ ............ ............ ............
# AdjClose  ............ ............ ............ ............ ............
# Volume^   ............ ............ ............ ............ ............
#
# *  : Data n/a 01 Jan 1990 - 28 Feb 2022
# ** : Data n/a 02 Jul 2022 - 30 Jul 2022
# ^ : Data missing

# currency row formatting
# e.g. #                                                             Currency
CUR_ROW_FMT = f'>{FORMAT_WIDTH_MARK}'
# title row formatting
# e.g Stock : IBM - International Business Machines Corporation           USD
#     1-----7                                                             1-3
TITLE_CELL_WIDTH = 7   # Stock/Period cell width
CUR_CELL_WIDTH = 3     # currency cell width
TITLE_ROW_FMT = f'<{FORMAT_WIDTH_MARK}'
TITLE_CELL_FMT = f'<{FORMAT_WIDTH_MARK}'
TITLE_TEXT_CELL_FMT = f'<{FORMAT_WIDTH_MARK}'
TITLE_CUR_CELL_FMT = f'>{FORMAT_WIDTH_MARK}'
# header row formatting
# e.g.               Min          Max         Change         %
HDR_CELL_FMT = f'^{FORMAT_WIDTH_MARK}'
# data row formatting
# e.g. Open      ............ ............ ............ ............
#      1-------9 1---------12
VALUE_NAME_CELL_WIDTH = 9   # Open/Low/High etc. cell width
DATA_CELL_WIDTH = 12
VALUE_NAME_FMT = f'<{FORMAT_WIDTH_MARK}'
DATA_CELL_FMT = f'>{FORMAT_WIDTH_MARK}'
# notes formatting
NOTE_1 = '*'
NOTE_2 = '*' * 2
NOTE_MARK_WIDTH = 2
NOTE_ROW_FMT = f'<{FORMAT_WIDTH_MARK}'
MISSING_DATA = '^'

CHANGE_STATS = [DfStat.CHANGE, DfStat.PERCENT_CHANGE]
STATS = [DfStat.MIN, DfStat.MAX, DfStat.AVG]
STATS.extend(CHANGE_STATS)

SYMBOL = 'symbol'
NAME = 'name'
CURRENCY = 'currency'
NAME_CURRENCY = [NAME, CURRENCY]


def display_single(results: dict):
    """
    Display single analysis results

    Args:
        results (dict): result to display
    """

    check_meta(results)

    grid = DGrid(MAX_LINE_LEN)

    # add currency title
    add_currency_title(grid)
    # add stock
    add_stock(grid, results)
    # add period
    add_period(grid, results)
    # add header
    add_header(grid)

    # add data row
    for column in DfColumn.NUMERIC_COLUMNS:

        row = DRow(grid.width)

        # value name
        name = f'{column.title}{MISSING_DATA}' if \
            drill_dict(results, 'data_na', column.title) else column.title
        cell = DCell(name, VALUE_NAME_CELL_WIDTH, fmt=VALUE_NAME_FMT)
        row.add_cell(cell)

        # stats
        for stat in STATS:
            cell = DCell(str(results[stat.column_key(column)]),
                            DATA_CELL_WIDTH, fmt=DATA_CELL_FMT)
            if stat in CHANGE_STATS:
                value = results[stat.column_key(column)]
                cell.set_marker(
                    Marker.UP if value > 0 else \
                        Marker.DOWN if value < 0 else None)

            row.add_cell(cell)

        grid.add_row(row)

    # add missing data notes
    add_missing_notes(grid, results)

    grid.display()


def add_header(grid: DGrid):
    """
    Add header row to grid

    Args:
        grid (DGrid): grid to add to
    """
    row = DRow(grid.width)

    # value name blank
    cell = DCell('', VALUE_NAME_CELL_WIDTH, fmt=HDR_CELL_FMT)
    row.add_cell(cell)

    # stat names
    for stat in STATS:
        cell = DCell(stat.short, DATA_CELL_WIDTH, fmt=HDR_CELL_FMT)
        row.add_cell(cell)

    grid.add_row(row)


def add_currency_title(grid: DGrid):
    """
    Add currency title row to grid

    Args:
        grid (DGrid): grid to add to
    """
    row = DRow(grid.width).set_fmt(CUR_ROW_FMT)
    row.add_cell(
        DCell('Currency', VALUE_NAME_CELL_WIDTH)
    )
    grid.add_row(row)


def add_title_row(grid: DGrid, title: str, cells: List[DCell]):
    """
    Add a title row to grid

    Args:
        grid (DGrid): grid to add to
        title (str): title to display
        text (str): text to display
    """
    row = DRow(grid.width).set_fmt(TITLE_ROW_FMT)
    title = title.ljust(TITLE_CELL_WIDTH - 1)
    row.add_cell(
        DCell(f'{title}:', TITLE_CELL_WIDTH)
    )
    row.add_cell(cells)
    grid.add_row(row)


def add_period(grid: DGrid, results: object):
    """
    Add currency title row to grid

    Args:
        grid (DGrid): grid to add to
        results (object): result to display
    """
    note1 = NOTE_1 if drill_dict(results, 'data_na', 'from', 'missing') \
                    else ''
    note2 = NOTE_2 if drill_dict(results, 'data_na', 'to', 'missing') else ''
    from_date = convert_date_time(results['from'], DateFormat.FRIENDLY_DATE)
    to_date = convert_date_time(results['to'], DateFormat.FRIENDLY_DATE)

    period = f"{from_date}{note1} - {to_date}{note2}"
    period_width = grid.width - grid.gap - TITLE_CELL_WIDTH
    add_title_row(grid, 'Period', [
        DCell(period, period_width, TITLE_TEXT_CELL_FMT)
    ])


def add_stock(grid: DGrid, results: object):
    """
    Add stock title row to grid

    Args:
        grid (DGrid): grid to add to
        results (object): result to display
    """
    stock = f"{results[SYMBOL]} - {results[NAME]}"
    stock_width = grid.width - (grid.gap * 2) - TITLE_CELL_WIDTH - \
                        CUR_CELL_WIDTH
    add_title_row(grid, 'Stock', [
        DCell(stock, stock_width, TITLE_TEXT_CELL_FMT),
        DCell(results[CURRENCY], CUR_CELL_WIDTH, TITLE_CUR_CELL_FMT)
    ])


def add_missing_notes(grid: DGrid, results: object):
    """
    Add missing data notes

    Args:
        grid (DGrid): grid to add to
        results (object): result to display
    """
    added_blank = False
    for note, prop in [(NOTE_1, 'from'), (NOTE_2, 'to')]:
        missing = results['data_na'][prop]
        if missing['missing']:
            from_date = \
                convert_date_time(missing['start'], DateFormat.FRIENDLY_DATE)
            to_date = \
                convert_date_time(missing['end'], DateFormat.FRIENDLY_DATE)
            text = f"{f'{note}':{f'<{NOTE_MARK_WIDTH}'}}: "\
                   f"Data n/a {from_date} - {to_date}"

            added_blank = _add_missing_notes_row(grid, text, added_blank)

    # missing data
    for column in DfColumn.NUMERIC_COLUMNS:
        if drill_dict(results, 'data_na', column.title):
            text = f"{f'{MISSING_DATA}':{f'<{NOTE_MARK_WIDTH}'}}: "\
                   f"Data missing"

            added_blank = _add_missing_notes_row(grid, text, added_blank)


def _add_missing_notes_row(grid: DGrid, text: str, added_blank: bool) -> bool:
    """
    Add a missing data note row

    Args:
        grid (DGrid): grid to add to
        text (str): cell text
        added_blank (bool): blank row has been added flag

    Returns:
        bool: blank row has been added
    """
    if not added_blank:
        grid.add_row(DRow.blank_row())
        added_blank = True

    row = DRow(grid.width)
    row.add_cell(
        DCell(text, row.width)
    )
    grid.add_row(row)

    return added_blank


def check_meta(results: dict):
    """
    Check meta data for stock

    Args:
        results (dict): result to display
    """
    meta = {
        key: None for key in NAME_CURRENCY
    }
    meta[SYMBOL] = drill_dict(results, SYMBOL)
    if meta[SYMBOL]:
        company = search_company(
                    meta[SYMBOL], CompanyColumn.SYMBOL, exact_match=True)
        if company:
            # have info in sheets
            assert company.num_items == 1, \
                f"{meta[SYMBOL]} symbol error; {company.num_items} results"

            company_info = company.get_current_page()[0]
            for key in NAME_CURRENCY:
                meta[key] = getattr(company_info, key)

        if not meta[NAME] or not meta[CURRENCY]:
            # get info from meta data api
            meta_data = download_meta_data(meta[SYMBOL])
            if meta_data:
                meta_name = drill_dict(
                    meta_data.data, 'result', 'shortName')
                if meta_name:
                    if meta_name != meta[NAME]:
                        # according to API docs, the 'Companies By Exchange'
                        # endpoint is 'Manually Populated List Of Common Stocks
                        # Per Exchange Code. Not Guaranteed To Be Up To Date'
                        # so use 'Live Stock Metadata' endpoint which is the
                        # 'real time metadata'
                        meta[NAME] = meta_name
                    else:
                        meta_name = None    # don't save

                if not meta[CURRENCY]:
                    # extract currency
                    meta[CURRENCY] = drill_dict(
                            meta_data.data, 'result', CURRENCY)

                save_stock_meta_data(
                    meta[SYMBOL], meta[CURRENCY], name=meta_name)

    else:
        meta[SYMBOL] = 'n/a'

    for key in NAME_CURRENCY:
        if not meta[key]:
            meta[key] = 'n/a'

    # add name/currency to results
    results.update(meta)
