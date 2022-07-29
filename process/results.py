"""
Processing results display functions
"""

from typing import List
from stock import DfStat, DfColumn
from utils import MAX_LINE_LEN, FRIENDLY_DATE_FMT
from .grid import DGrid, DCell, DRow, FORMAT_WIDTH_MARK, Marker


# 80 Columns
# 12345678901234567890123456789012345678901234567890123456789012345678901234567890

#                                                                        Currency
# Stock : IBM - International Business Machines Corporation                   USD
# Period: 01 Mar 2022 - 01 Jul 2022
#               Min          Max         Change         %
# Open      ............ ............ ............ ............
# Low       ............ ............ ............ ............
# High      ............ ............ ............ ............
# Close     ............ ............ ............ ............
# AdjClose  ............ ............ ............ ............
# Volume    ............ ............ ............ ............

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

CHANGE_STATS = [DfStat.CHANGE, DfStat.PERCENT_CHANGE]
STATS = [DfStat.MIN, DfStat.MAX]
STATS.extend(CHANGE_STATS)

def display_single(results: object):
    """
    Display single analysis results

    Args:
        results (object): result to display
    """

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
        cell = DCell(column.title, VALUE_NAME_CELL_WIDTH, fmt=VALUE_NAME_FMT)
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
    period = f"{results['from'].strftime(FRIENDLY_DATE_FMT)} - "\
             f"{results['to'].strftime(FRIENDLY_DATE_FMT)}"
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
    stock = f"{results['symbol'] if 'symbol' in results else 'n/a'} - "\
            f"Coming soon name Ltd."
    stock_width = grid.width - (grid.gap * 2) - TITLE_CELL_WIDTH - \
                        CUR_CELL_WIDTH
    add_title_row(grid, 'Stock', [
        DCell(stock, stock_width, TITLE_TEXT_CELL_FMT),
        DCell('CUR', CUR_CELL_WIDTH, TITLE_CUR_CELL_FMT)
    ])
