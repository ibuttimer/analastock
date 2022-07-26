"""
Stock analysis related functions
"""
from datetime import date, datetime, timedelta
import re
from typing import Callable, List, Union
from collections import namedtuple

import pandas as pd
from utils import get_input, error, ABORT, last_day_of_month
from .data import StockDownload, StockParam
from .enums import DfColumn, DfStat, AnalysisRange


DATE_SEP = '-'
DATE_FORM = f'dd{DATE_SEP}mm{DATE_SEP}yyyy'
DATE_FORMAT = f'%d{DATE_SEP}%m{DATE_SEP}%Y'
DATE_FMT = '{day}'+DATE_SEP+'{mth}'+DATE_SEP+'{year}'
FRIENDLY_FORMAT = '%d %b %Y'

MIN_DATE = datetime(1962, 2, 1)

SYMBOL_HELP = f"Enter symbol for the stock required, or '{ABORT}' to cancel.\n"\
              f"e.g. IBM: International Business Machines Corporation"
FROM_DATE_HELP = f"Enter analysis start date, or '{ABORT}' to cancel"
TO_DATE_HELP = f"Enter analysis end date, or '{ABORT}' to cancel"
PERIOD_HELP = f"Enter period in the form, [period] [from|to|ytd] [{DATE_FORM}], or\n"\
              f"'{ABORT}' to cancel.\n"\
              f"where: [period]      - is of the form '[0-9][d|m|y]' "\
                f"with 'd' for day,\n"\
              f"                       'm' for month and 'y' for year.\n"\
              f"                       e.g. '5d' is 5 days\n"\
              f"       [from|to|ytd] - 'from'/'to' date or 'year-to-date' date. \n"\
              f"                       Note: [period] not required for 'ytd'.\n"\
              f"                       e.g. 'ytd {datetime.now().strftime(DATE_FORMAT)}'\n"\
              f"       [{DATE_FORM}]  - date, or today if omitted"

DMY_REGEX = re.compile(rf"^(\d)([dmy])\s+(\w+)\s+(\d+){DATE_SEP}(\d+){DATE_SEP}(\d+)")
DMY_NOW_REGEX = re.compile(r"^(\d)([dmy])\s+(\w+)")
YTD_REGEX = re.compile(rf"^(\w+)\s+(\d+){DATE_SEP}(\d+){DATE_SEP}(\d+)")
YTD_NOW_REGEX = re.compile(r"^(\w+)")
PERIOD_KEYS = [
            'num',          # (int): unit count
            'time_unit',    # (str): time unit; d/m/y
            'time_dir',     # (str): direction; from/to
            'day',          # (int): day
            'month',        # (int): month
            'year'          # (int): year
        ]
""" Period param object keys as per DMY_REGEX """
DIR_KEY_IDX = 2
DAY_KEY_IDX = 3

PRICE_PRECISION = 6
""" Precision for stock prices """
PERCENT_PRECISION = 2
""" Precision for percentages """

Period = namedtuple("Period", ['from_date', 'to_date'])


def validate_date(date_string: str) -> Union[datetime, None]:
    """
    Validate a date string

    Args:
        date_string (str): input date string

    Returns:
        Union[datetime, None]: datetime object if valid, otherwise None
    """
    date_time = None
    try:
        date_time = datetime.strptime(date_string, DATE_FORMAT)

        if date_time > datetime.now():
            error('Invalid date: future date')
            date_time = None
        if date_time < MIN_DATE:
            error(
                f"Invalid date: shouldn't be prior to "
                f"{MIN_DATE.strftime(FRIENDLY_FORMAT)}"
            )
            date_time = None

    except ValueError:
        error(f'Invalid date: required format is {DATE_FORM}')

    return date_time


def validate_date_after(
        limit_datetime: datetime) -> Callable[[str], Union[datetime, None]]:
    """
    Decorator to validate a date and ensure its after the specified date

    Args:
        limit_datetime (datetime): must be after date

    Returns:
        Callable[[str], Union[datetime, None]]: validation function
    """
    def validate_func(date_string: str) -> datetime:
        """
        Validate a date string is after the from date

        Args:
            date_string (str): input date string

        Returns:
            Union[datetime, None]: datetime object if valid, otherwise None
        """
        date_time = validate_date(date_string)
        if date_time and date_time < limit_datetime:
            date_time = None
            error(
                f'Invalid date: must be after '
                f'{limit_datetime.strftime(FRIENDLY_FORMAT)}'
            )

        return date_time

    return validate_func


def validate_symbol(symbol: str) -> Union[str, None]:
    """
    Validate a symbol string

    Args:
        symbol (str): input symbol string

    Returns:
        Union[str, None]: string object if valid, otherwise None
    """
    if symbol.startswith('^'):
        error('Analysis of stock indices is not supported')
        symbol = None

    return symbol


def validate_period(period_str: str) -> Union[Period, None]:
    """
    Validate a period string

    Args:
        period_str (str): input period string

    Returns:
        Union[Period, None]: string object if valid, otherwise None
    """
    period = None
    period_str = period_str.strip().lower()
    params = period_param_template()

    # check formats like '1d from dd-mm-yyyy'
    match = DMY_REGEX.match(period_str)
    if match:
        # period keys follows regex group order of DMY_REGEX
        for idx, key in enumerate(PERIOD_KEYS):
            params[key] = match.group(idx + 1)

        period = make_dmy_period(params)

    if not match:
        # check formats with omitted date like '1d from'
        match = DMY_NOW_REGEX.match(period_str)
        if match:
            # period keys follows regex group order of DMY_NOW_REGEX
            # excluding day/mth/year at end
            for idx, key in enumerate(PERIOD_KEYS):
                if idx < DAY_KEY_IDX:
                    params[key] = match.group(idx + 1)

            period = make_dmy_period(params)

    if not match:
        # check formats like 'ytd dd-mm-yyyy'
        match = YTD_REGEX.match(period_str)
        if match:
            # dir/day/mth/year period keys at end,
            # follow regex group order of YTD_REGEX
            for idx in range(DIR_KEY_IDX, len(PERIOD_KEYS)):
                params[PERIOD_KEYS[idx]] = match.group(idx - DIR_KEY_IDX + 1)

            period = make_dmy_period(params)

    if not match:
        # check formats with omitted date like 'ytd'
        match = YTD_NOW_REGEX.match(period_str)
        if match:
            # dir/day/mth/year period keys at end,
            # follow regex group order of YTD_REGEX
            params[PERIOD_KEYS[DIR_KEY_IDX]] = match.group(1)

            period = make_dmy_period(params)

    if not period:
        error('Invalid period')

    return period


def period_param_template() -> object:
    """ Generate period parameter object template """
    return { key: None for key in PERIOD_KEYS }


def make_dmy_period(params: object) -> Union[Period, None]:
    """
    Generate a day-month-year period

    Args:
        params (object): object of the form generated by
                         period_param_template()

    Returns:
        Union[Period, None]: period or None of invalid
    """
    period = None

    # rudimentary checks
    valid = params['time_dir'] in ['from', 'to', 'ytd']
    if valid:

        is_fwd = params['time_dir'] == 'from'
        num = (int(params['num']) if params['num'] else 0) * (1 if is_fwd else -1)
        time_unit = params['time_unit']
        # default to today's date
        today = datetime.now()
        day = int(params['day']) if params['day'] else today.day
        month = int(params['month']) if params['month'] else today.month
        year = int(params['year']) if params['year'] else today.year

        in_date = validate_date(DATE_FMT.format(day=day, mth=month, year=year))
        if in_date:
            if time_unit == 'd':
                # days
                out_date = in_date + timedelta(days=num)
            elif time_unit == 'm':
                # months
                out_date = in_date

                # original was last day of month flag
                mth_last_day = in_date.day == last_day_of_month(in_date.year, in_date.month)

                def not_december(chk_mth):
                    """ True if month is not December """
                    return chk_mth < 12

                def not_january(chk_mth):
                    """ True if month is not January """
                    return chk_mth > 1

                if is_fwd:
                    step = 1    # step forward from
                    not_new_year = not_december # no new year if not december
                else:
                    step = -1   # step back to
                    not_new_year = not_january # no new year if not january

                num = num if num > 0 else -num  # positive loop control
                while num > 0:
                    no_new_year = not_new_year(out_date.month)

                    yr_val = out_date.year + (0 if no_new_year else step)
                    mth_val = out_date.month + step if no_new_year else \
                                                1 if out_date.month == 12 else 12
                    # day doesn't change when < 28
                    # stays at last day of month, if original was last day of month
                    # last day of new month, if original > last day of new month
                    # otherwise original day
                    new_mth_last_day = last_day_of_month(yr_val, mth_val)
                    day_val = in_date.day if in_date.day < 28 else \
                            new_mth_last_day if mth_last_day else \
                                new_mth_last_day if in_date.day > new_mth_last_day else in_date.day

                    out_date = out_date.replace(year=yr_val, month=mth_val, day=day_val)
                    num -= 1

            elif time_unit == 'y':
                # years
                out_date = in_date.replace(year=in_date.year + num)
            elif params['time_dir'] == 'ytd':
                out_date = datetime(year=in_date.year, month=1, day=1)
                valid = out_date < in_date
            else:
                valid = False

            if valid:
                period = Period(in_date, out_date) if is_fwd else Period(out_date, in_date)
                valid = period.from_date < period.to_date and \
                            period.to_date.date() <= datetime.now().date()
                if not valid:
                    period = None

    return period


def get_period_range(stock_param: StockParam) -> StockParam:
    """
    Get date range for stock parameters

    Args:
        stock_param (StockParam): stock parameters

    Returns:
        StockParam: stock parameters
    """
    period = get_input(
        'Enter period',
        validate=validate_period,
        help_text=PERIOD_HELP
    )

    if period == ABORT:
        stock_param = None
    elif isinstance(period, Period):
        stock_param.from_date = period.from_date
        stock_param.to_date = period.to_date
    else:
        stock_param = None

    return stock_param


def get_date_range(stock_param: StockParam) -> StockParam:
    """
    Get time period range for stock parameters

    Args:
        stock_param (StockParam): stock parameters

    Returns:
        StockParam: stock parameters
    """
    entered_date = get_input(
        'Enter from date',
        validate=validate_date,
        help_text=FROM_DATE_HELP,
        input_form=[DATE_FORM]
    )
    if entered_date != ABORT:
        stock_param.from_date = entered_date

        entered_date = get_input(
            'Enter to date (excluded)',
            validate=validate_date_after(stock_param.from_date),
            help_text=TO_DATE_HELP,
            input_form=[DATE_FORM]
        )
        if entered_date != ABORT:
            stock_param.to_date = entered_date

    if entered_date == ABORT:
        stock_param = None

    return stock_param


def get_stock_param(
        symbol: str = None, anal_rng: AnalysisRange = AnalysisRange.DATE) -> StockParam:
    """
    Get stock parameters

    Args:
        symbol (str, optional): stock symbol. Defaults to None.
        range (AnalysisRange, optional): Range entry method. Defaults to AnalysisRange.DATE.

    Returns:
        StockParam: stock parameters
    """
    stock_param = None

    if not symbol:
        symbol = get_input(
            'Enter stock symbol', validate=validate_symbol,
            help_text=SYMBOL_HELP
        )

    if symbol != ABORT:
        stock_param = StockParam(symbol)

        stock_param = get_date_range(stock_param) \
            if anal_rng == AnalysisRange.DATE else get_period_range(stock_param)

    return stock_param


def analyse_stock(
        data_frame: Union[pd.DataFrame, List[str], StockDownload]) -> dict:
    """
    Analyse stock data

    Args:
        data_frame (Union[Pandas.DataFrame, List[str], StockDownload]): data to analyse

    Returns:
        dict: dict of analysis results, like {
            'OpenMin': 11.34,
            'OpenMax': 12.34,
            'OpenChange': 1.0,
            'OpenPercentChange': 8.82,
            .....
        }
    """
    if isinstance(data_frame, StockDownload):
        # take analysis info from data class
        analyse = data_frame.data_frame
        from_date = data_frame.stock_param.from_date
        to_date = data_frame.stock_param.to_date
    else:
        # raw analysis and take date info from data
        analyse = data_frame
        from_date = None
        to_date = None
    if isinstance(analyse, list):
        analyse = StockDownload.list_to_frame(analyse)    # convert list to data frame

    # data in chronological order
    analyse.sort_values(by=DfColumn.DATE.title, ascending=True, inplace=True)
    if not from_date:
        # get date info for raw analysis
        from_date = analyse[DfColumn.DATE.title].min()
        to_date = analyse[DfColumn.DATE.title].max()
    else:
        # filter by min & max dates
        analyse = analyse[(analyse[DfColumn.DATE.title] >= from_date) &
                    (analyse[DfColumn.DATE.title] <= to_date)]

    analysis = {
        'from': from_date if isinstance(from_date, date) else from_date.date(),
        'to': to_date if isinstance(to_date, date) else to_date.date()
    }

    for column in DfColumn.NUMERIC_COLUMNS:
        data_series = analyse[column.title]

        # min value
        analysis[DfStat.MIN.column_key(column)] = data_series.min()

        # max value
        analysis[DfStat.MAX.column_key(column)] = data_series.max()

        # change
        change = round_price(data_series.iat[0] - data_series.iat[len(data_series)-1])
        analysis[DfStat.CHANGE.column_key(column)] = change

        # percentage change
        analysis[DfStat.PERCENT_CHANGE.column_key(column)] = round(
            (change / data_series.iat[0]) * 100, PERCENT_PRECISION
        )

    print(analysis)


def round_price(price: float) -> float:
    """
    Round a stock price

    Args:
        price (float): stock price

    Returns:
        float: rounded value
    """
    return round(price, PRICE_PRECISION)
