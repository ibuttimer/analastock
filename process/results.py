"""
Processing results display functions
"""

from typing import List, Union
from stock import (
    DfStat, DfColumn, CompanyColumn, DataMode, download_meta_data
)
from sheets import search_all, save_stock_meta_data
from utils import MAX_LINE_LEN, convert_date_time, DateFormat, drill_dict
from .grid import DGrid, DCell, DRow, FORMAT_WIDTH_MARK, Marker


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
STOCK_CELL_WIDTH = 5
STOCK_NAME_FMT = f'<{FORMAT_WIDTH_MARK}'
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


def display_single(result: dict):
    """
    Display single analysis results
    See https://github.com/ibuttimer/analastock/blob/main/design/design.md#analysis-result-single-company

    Args:
        result (dict): result to display
    """

    check_meta(result)

    grid = DGrid(MAX_LINE_LEN)

    # add currency title
    add_currency_title(grid)
    # add stock
    add_stock(grid, result)
    # add period
    add_period(grid, result)
    # add header
    add_header(grid)

    # add data row
    for column in DfColumn.NUMERIC_COLUMNS:

        row = DRow(grid.width)

        # value name
        name = f'{column.title}{MISSING_DATA}' if \
            column_data_missing(result, column) else column.title
        cell = DCell(name, VALUE_NAME_CELL_WIDTH, fmt=VALUE_NAME_FMT)
        row.add_cell(cell)

        # stats
        for stat in STATS:
            cell = DCell(str(result[stat.column_key(column)]),
                            DATA_CELL_WIDTH, fmt=DATA_CELL_FMT)
            if stat in CHANGE_STATS:
                value = result[stat.column_key(column)]
                cell.set_marker(
                    Marker.UP if value > 0 else \
                        Marker.DOWN if value < 0 else None)

            row.add_cell(cell)

        grid.add_row(row)

    # add missing data notes
    add_missing_notes(grid, result)

    grid.display()


def display_multiple(results: List[dict]):
    """
    Display multi analysis results
    See https://github.com/ibuttimer/analastock/blob/main/design/design.md#analysis-result-multiple-companies

    Args:
        results (List[dict]): result to display
    """
    is_multi = isinstance(results, list)

    check_meta(results)

    grid = DGrid(MAX_LINE_LEN)

    # add currency title
    add_currency_title(grid)

    for index, result in enumerate(results):
        # add stock
        add_stock(grid, result, mark = index + 1)
        # add period
        add_period(grid, result)

    # add header
    add_header(grid, is_multi=is_multi)

    # add data rows
    for column in DfColumn.NUMERIC_COLUMNS:
        for idx, result in enumerate(results):

            row = DRow(grid.width)

            # value name
            if idx == 0:
                cell = DCell(
                    column.title, VALUE_NAME_CELL_WIDTH, fmt=VALUE_NAME_FMT)
            else:
                cell = DCell.blank_cell(VALUE_NAME_CELL_WIDTH)
            row.add_cell(cell)

            if is_multi:
                # add stock marker
                missing = MISSING_DATA \
                    if column_data_missing(result, column) else ""
                cell = DCell(f'{result["marker"]}{missing}',
                                STOCK_CELL_WIDTH, fmt=STOCK_NAME_FMT)
                row.add_cell(cell)

            # stats
            for stat in STATS:
                cell = DCell(str(result[stat.column_key(column)]),
                                DATA_CELL_WIDTH, fmt=DATA_CELL_FMT)
                if stat in CHANGE_STATS:
                    value = result[stat.column_key(column)]
                    cell.set_marker(
                        Marker.UP if value > 0 else \
                            Marker.DOWN if value < 0 else None)

                row.add_cell(cell)

            grid.add_row(row)

    # add missing data notes
    add_missing_notes(grid, results)

    grid.display()


def add_header(grid: DGrid, is_multi: bool = False):
    """
    Add header row to grid

    Args:
        grid (DGrid): grid to add to
    """
    row = DRow(grid.width)

    # value name blank
    cell = DCell('', VALUE_NAME_CELL_WIDTH, fmt=HDR_CELL_FMT)
    row.add_cell(cell)

    if is_multi:
        # add stock header
        cell = DCell('Stock', STOCK_CELL_WIDTH, fmt=STOCK_NAME_FMT)
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


def add_period(grid: DGrid, result: dict):
    """
    Add period row to grid

    Args:
        grid (DGrid): grid to add to
        result (dict): result to display
    """
    note1 = NOTE_1 if data_is_missing(result, 'from') else ''
    note2 = NOTE_2 if data_is_missing(result, 'to') else ''
    from_date = convert_date_time(result['from'], DateFormat.FRIENDLY_DATE)
    to_date = convert_date_time(result['to'], DateFormat.FRIENDLY_DATE)

    period = f"{from_date}{note1} - {to_date}{note2}"
    period_width = grid.width - grid.gap - TITLE_CELL_WIDTH
    add_title_row(grid, 'Period', [
        DCell(period, period_width, TITLE_TEXT_CELL_FMT)
    ])


def add_stock(grid: DGrid, result: dict, mark: int = None):
    """
    Add stock title row to grid

    Args:
        grid (DGrid): grid to add to
        result (dict): result to display
    """
    marker = f'{mark}]' if mark else None
    stock = f"{f'{marker} ' if mark else ''}"\
            f"{result[SYMBOL]} - {result[NAME]}"
    stock_width = grid.width - (grid.gap * 2) - TITLE_CELL_WIDTH - \
                        CUR_CELL_WIDTH
    add_title_row(grid, 'Stock', [
        DCell(stock, stock_width, TITLE_TEXT_CELL_FMT),
        DCell(result[CURRENCY], CUR_CELL_WIDTH, TITLE_CUR_CELL_FMT)
    ])

    # add marker to result
    result['marker'] = marker


def add_missing_notes(grid: DGrid, results: Union[dict, List[dict]]):
    """
    Add missing data notes

    Args:
        grid (DGrid): grid to add to
        results (Union[dict, List[dict]]): results to display
    """
    is_multi = isinstance(results, list)
    if not is_multi:
        results = [results]

    added_blank = False

    for note, prop in [(NOTE_1, 'from'), (NOTE_2, 'to')]:
        added_note = False
        for result in results:

            missing = data_missing_info(result, prop)
            if missing['missing']:
                from_date = \
                    convert_date_time(missing['start'],
                                        DateFormat.FRIENDLY_DATE)
                to_date = \
                    convert_date_time(missing['end'], DateFormat.FRIENDLY_DATE)
                note_text = '' if added_note else f'{note}'
                marker = f"{result['marker']} " if is_multi else ""
                text = \
                    f"{f'{note_text}':{f'<{NOTE_MARK_WIDTH}'}}: "\
                    f"{marker}Data n/a {from_date} - {to_date}"

                added_blank = _add_missing_notes_row(grid, text, added_blank)

    # missing data
    added_missing = False
    for result in results:
        for column in DfColumn.NUMERIC_COLUMNS:
            if column_data_missing(result, column):
                text = f"{f'{MISSING_DATA}':{f'<{NOTE_MARK_WIDTH}'}}: "\
                    f"Data missing"

                added_blank = _add_missing_notes_row(grid, text, added_blank)
                added_missing = True
                break

        if added_missing:
            break

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


def check_meta(results: Union[dict, List[dict]]):
    """
    Check meta data for stock

    Args:
        results (Union[dict, List[dict]]): results to display
    """
    if isinstance(results, dict):
        results = [results]

    for result in results:
        meta = {
            key: None for key in NAME_CURRENCY
        }
        meta[SYMBOL] = drill_dict(result, SYMBOL)
        if meta[SYMBOL]:
            pg_entity = search_all(
                        meta[SYMBOL], CompanyColumn.SYMBOL, exact_match=True)
            if pg_entity:
                # have info in sheets
                assert pg_entity.num_items == 1, \
                    f"{meta[SYMBOL]} symbol error; "\
                    f"{pg_entity.num_items} results"

                entity_info = pg_entity.get_current_page()[0]
                for key in NAME_CURRENCY:
                    meta[key] = getattr(entity_info, key)

            if not meta[NAME] or not meta[CURRENCY]:
                # get info from meta data api

                # TODO add data_mode to all elements in flow

                meta_data = download_meta_data(meta[SYMBOL],
                                            data_mode=DataMode.LIVE_SAVE_SAMPLE
                                            # data_mode=DataMode.SAMPLE
                                            )
                if meta_data and meta_data.response_ok:
                    meta_name = drill_dict(meta_data.data, 'shortName')
                    if meta_name:
                        if meta_name != meta[NAME]:
                            # according to API docs, the 'Companies By
                            # Exchange' endpoint is 'Manually Populated
                            # List Of Common Stocks Per Exchange Code. Not
                            # Guaranteed To Be Up To Date', so use 'Live Stock
                            # Metadata' endpoint which is the 'real time
                            # metadata',
                            # and for other entities 'real time metadata' is
                            # the only source
                            meta[NAME] = meta_name
                        else:
                            meta_name = None    # don't save

                    if not meta[CURRENCY]:
                        # extract currency
                        meta[CURRENCY] = drill_dict(meta_data.data, CURRENCY)

                    save_stock_meta_data(
                        meta[SYMBOL], meta[CURRENCY], name=meta_name,
                        meta=meta_data.data)

        else:
            meta[SYMBOL] = 'n/a'

        for key in NAME_CURRENCY:
            if not meta[key]:
                meta[key] = 'n/a'

        # add name/currency to result
        result.update(meta)


def column_data_missing(result: dict, column: DfColumn) -> bool:
    """
    Check if column data missing

    Args:
        result (dict): result to display
        column (DfColumn): column to check

    Returns:
        bool: True if data missing
    """
    return drill_dict(result, 'data_na', column.title)


def data_missing_info(result: dict, prop: str) -> dict:
    """
    Get the data missing information

    Args:
        result (dict): result to display
        prop (str): date property; 'from'/'to'

    Returns:
        dict: information
    """
    return drill_dict(result, 'data_na', prop)
    # return drill_dict(result, 'data_na', prop, 'missing')


def data_is_missing(result: dict, prop: str) -> bool:
    """
    Get the data missing flag

    Args:
        result (dict): result to display
        prop (str): date property; 'from'/'to'

    Returns:
        bool: True if data missing
    """
    return data_missing_info(result, prop)['missing']

