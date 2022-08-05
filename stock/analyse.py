"""
Stock analysis related functions
"""
from datetime import date, datetime, timedelta
import re
from typing import Callable, List, Tuple, Union
from collections import namedtuple

import pandas as pd
from utils import (
    get_input, error, ABORT, last_day_of_month, FRIENDLY_DATE_FMT,
    filter_data_frame_by_date, convert_date_time, DateFormat
)
from .data import StockDownload, StockParam
from .enums import DfColumn, DfStat, AnalysisRange


DATE_SEP = '-'
DATE_FORM = f'dd{DATE_SEP}mm{DATE_SEP}yyyy'
DATE_FORMAT = f'%d{DATE_SEP}%m{DATE_SEP}%Y'
DATE_FMT = '{day}'+DATE_SEP+'{mth}'+DATE_SEP+'{year}'

MIN_DATE = datetime(1962, 2, 1)

SYMBOL_HELP = f"Enter symbol for the stock required, or '{ABORT}' to cancel.\n"\
              f"e.g. IBM: International Business Machines Corporation"
FROM_DATE_HELP = f"Enter analysis start date, or '{ABORT}' to cancel"
TO_DATE_HELP = f"Enter analysis end date (excluded from analysis), "\
               f"or '{ABORT}' to cancel"
PERIOD_HELP = f"Enter period in either of the following forms:\n"\
              f"   - '[period] [from|to|ytd] [{DATE_FORM}]'\n"\
              f"   - '[{DATE_FORM}] [from|to] [{DATE_FORM}]'\n"\
              f"or enter '{ABORT}' to cancel.\n"\
              f"where: [period]      - is of the form '[0-9][d|w|m|y]' "\
                f"with 'd' for day,\n"\
              f"                       'w' for week, 'm' for month and "\
                f"'y' for year.\n"\
              f"                       e.g. '5d' is 5 days\n"\
              f"       [from|to|ytd] - 'from'/'to' date or 'year-to-date' "\
                f"date.\n"\
              f"                       Note: [period] not required for "\
                f"'ytd'.\n"\
              f"                       e.g. 'ytd "\
                f"{datetime.now().strftime(DATE_FORMAT)}'\n"\
              f"       [{DATE_FORM}]  - date, or today if omitted"

DATE_REGEX = rf"(\d+){DATE_SEP}(\d+){DATE_SEP}(\d+)"
PERIOD_REGEX = r"(\d+)([dwmy])"
DMY_DMY_REGEX = re.compile(
    rf"^\s*{DATE_REGEX}\s+(\w+)\s+{DATE_REGEX}\s*$")
DMY_REGEX = re.compile(
    rf"^\s*{PERIOD_REGEX}\s+(\w+)\s+{DATE_REGEX}\s*$")
DMY_NOW_REGEX = re.compile(rf"^\s*{PERIOD_REGEX}\s+(\w+)\s*$")
YTD_REGEX = re.compile(rf"^\s*(\w+)\s+{DATE_REGEX}\s*$")
YTD_NOW_REGEX = re.compile(r"^\s*(\w+)\s*$")
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

LT = '<'
LTE = '<='
EQ = '=='
GTE = '>='
GT = '>'
VAL_DATE_LMT_MSG = {
    key: value for key, value in [
        (LT, 'before'), (LTE, 'less than or equal'), (EQ, 'equal to'),
        (GTE, 'greater than or equal'), (GT, 'after')
    ]
}


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
        elif date_time < MIN_DATE:
            error(
                f"Invalid date: shouldn't be prior to "
                f"{MIN_DATE.strftime(FRIENDLY_DATE_FMT)}"
            )
            date_time = None

    except ValueError:
        error(f'Invalid date: required format is {DATE_FORM}')

    return date_time


def validate_date_limit(
        limit_datetime: datetime,
        check: str) -> Callable[[str], Union[datetime, None]]:
    """
    Decorator to validate a date and ensure passes passes ``check``
    against the specified date

    Args:
        limit_datetime (datetime): date to pass check of
        check (str): check to perform; '<', '<=', '==', '>=' or '>'

    Returns:
        Callable[[str], Union[datetime, None]]: validation function
    """
    def validate_func(date_string: str) -> datetime:
        """
        Validate a date string passes check against the limit date

        Args:
            date_string (str): input date string

        Returns:
            Union[datetime, None]: datetime object if valid, otherwise None
        """
        date_time = validate_date(date_string)
        if check in VAL_DATE_LMT_MSG:
            # test error condition
            if check == LT:
                is_error = date_time >= limit_datetime
            elif check == LTE:
                is_error = date_time > limit_datetime
            elif check == EQ:
                is_error = date_time != limit_datetime
            elif check == GTE:
                is_error = date_time < limit_datetime
            elif check == GT:
                is_error = date_time <= limit_datetime
        else:
            raise ValueError(f'Unknown check: {check}')

        if date_time and is_error:
            date_time = None
            error(
                f'Invalid date: must be {VAL_DATE_LMT_MSG[check]} '
                f'{limit_datetime.strftime(FRIENDLY_DATE_FMT)}'
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

    for regex_idx, regex in enumerate([
            # check formats like 'dd-mm-yyyy to dd-mm-yyyy'
            DMY_DMY_REGEX,
            # check formats like '1d from dd-mm-yyyy'
            DMY_REGEX,
            # check formats with omitted date like '1d from'
            DMY_NOW_REGEX,
            # check formats like 'ytd dd-mm-yyyy'
            YTD_REGEX,
            # check formats with omitted date like 'ytd'
            YTD_NOW_REGEX
        ]):
        match = regex.match(period_str)
        if match:
            params = period_param_template()

            if regex_idx == 0:
                # check formats like 'dd-mm-yyyy to dd-mm-yyyy'
                # day/mth/year period keys at end,
                # follow regex group order of DMY_DMY_REGEX
                # d:1 m:2 y:3 to:4 d:5 m:6 y:7
                params2 = period_param_template()
                for idx in range(DAY_KEY_IDX, len(PERIOD_KEYS)):
                    key = PERIOD_KEYS[idx]
                    group = idx - DAY_KEY_IDX + 1
                    params[key] = match.group(group)
                    params2[key] = match.group(group + 4)

                period = get_dmy_dmy_period(
                            params, match.group(4), params2)
            elif regex_idx == 1:
                # check formats like '1d from dd-mm-yyyy'
                # period keys follows regex group order of DMY_REGEX
                for idx, key in enumerate(PERIOD_KEYS):
                    params[key] = match.group(idx + 1)
            elif regex_idx == 2:
                # check formats with omitted date like '1d from'
                # period keys follows regex group order of DMY_NOW_REGEX
                # excluding day/mth/year at end
                for idx, key in enumerate(PERIOD_KEYS):
                    if idx < DAY_KEY_IDX:
                        params[key] = match.group(idx + 1)
            elif regex_idx == 3:
                # check formats like 'ytd dd-mm-yyyy'
                # dir/day/mth/year period keys at end,
                # follow regex group order of YTD_REGEX
                for idx in range(DIR_KEY_IDX, len(PERIOD_KEYS)):
                    params[PERIOD_KEYS[idx]] =\
                        match.group(idx - DIR_KEY_IDX + 1)
            elif regex_idx == 4:
                # check formats with omitted date like 'ytd'
                # dir/day/mth/year period keys at end,
                # follow regex group order of YTD_REGEX
                params[PERIOD_KEYS[DIR_KEY_IDX]] = match.group(1)

            if regex_idx > 0:
                period = make_dmy_period(params)

            if period:
                break
    else:
        error('Invalid period')

    return period


def period_param_template() -> dict:
    """ Generate period parameter object template """
    return { key: None for key in PERIOD_KEYS }


def param_date(params: dict) -> Tuple[int]:
    """
    Unpack date elements from ``param``

    Args:
        params (dict): object of the form generated by
                         period_param_template()

    Returns:
        Tuple[int]: day, month, year
    """
    # default to today's date
    today = datetime.now()
    day = int(params['day']) if params['day'] else today.day
    month = int(params['month']) if params['month'] else today.month
    year = int(params['year']) if params['year'] else today.year
    return day, month, year


def make_dmy_period(params: dict) -> Union[Period, None]:
    """
    Generate a day-month-year period

    Args:
        params (dict): object of the form generated by
                         period_param_template()

    Returns:
        Union[Period, None]: period or None of invalid
    """
    period = None

    # rudimentary checks
    valid = params['time_dir'] in ['from', 'to', 'ytd']
    if valid:

        is_fwd = params['time_dir'] == 'from'
        num = (int(params['num'])\
                if params['num'] else 0) * (1 if is_fwd else -1)
        time_unit = params['time_unit']
        # default to today's date
        day, month, year = param_date(params)

        in_date = validate_date(DATE_FMT.format(day=day, mth=month, year=year))
        if in_date:
            if time_unit == 'd':
                # days
                out_date = in_date + timedelta(days=num)
            elif time_unit == 'w':
                # weeks
                out_date = in_date + timedelta(days=num * 7)
            elif time_unit == 'm':
                # months
                out_date = in_date

                # original was last day of month flag
                mth_last_day = \
                    in_date.day == last_day_of_month(
                                in_date.year, in_date.month)

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
                    mth_val = out_date.month + step \
                        if no_new_year else 1 if out_date.month == 12 else 12
                    # day doesn't change when < 28
                    # stays at last day of month, if original was last day
                    # of month
                    # last day of new month, if original > last day of
                    # new month
                    # otherwise original day
                    new_mth_last_day = last_day_of_month(yr_val, mth_val)
                    day_val = in_date.day if in_date.day < 28 else \
                            new_mth_last_day if mth_last_day else \
                                new_mth_last_day \
                                    if in_date.day > new_mth_last_day \
                                    else in_date.day

                    out_date = out_date.replace(
                                year=yr_val, month=mth_val, day=day_val)
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
                period = Period(in_date, out_date) \
                            if is_fwd else Period(out_date, in_date)
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
        stock_param.set_from_date(period.from_date)
        stock_param.set_to_date(period.to_date)
    else:
        stock_param = None

    return stock_param


def get_dmy_dmy_period(params: dict, preposition: str,
                        params2: dict) -> Union[Period, None]:
    """
    Get time period range for stock parameters

    Args:
        params (dict): object of the form generated by
                         period_param_template()
        preposition (str): preposition
        params2 (dict): object of the form generated by
                         period_param_template()

    Returns:
        StockParam: stock parameters
    """
    period = None

    day, month, year = param_date(params)
    in_date = validate_date(DATE_FMT.format(day=day, mth=month, year=year))

    preposition = preposition.lower()

    day, month, year = param_date(params2)
    out_date = validate_date(DATE_FMT.format(day=day, mth=month, year=year))

    if in_date and out_date and preposition in ['from', 'to']:
        if validate_date_limit(in_date,
                GT if preposition == 'to' else LT)(
                    out_date.strftime(DATE_FORMAT)
                ):
            period = Period(in_date, out_date)

    return period


def get_date_range(stock_param: StockParam) -> StockParam:
    """
    Get time period range for stock parameters

    Args:
        stock_param (StockParam): stock parameters

    Returns:
        StockParam: stock parameters
    """
    entered_date = get_input(
        'Enter from date         ',
        validate=validate_date,
        help_text=FROM_DATE_HELP,
        input_form=[DATE_FORM]
    )
    if entered_date != ABORT:
        stock_param.set_from_date(entered_date)

        entered_date = get_input(
            'Enter to date (excluded)',
            validate=validate_date_limit(stock_param.from_date, LTE),
            help_text=TO_DATE_HELP,
            input_form=[DATE_FORM]
        )
        if entered_date != ABORT:
            stock_param.set_to_date(entered_date)

    if entered_date == ABORT:
        stock_param = None

    return stock_param


def get_stock_param_symbol(symbol: str = None) -> StockParam:
    """
    Get symbol for stock parameters

    Args:
        symbol (str, optional): Stock symbol. Defaults to None.

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

    return stock_param


def get_stock_param_range(
        stock_param: StockParam,
        anal_rng: AnalysisRange = AnalysisRange.DATE,
        range_select: Callable[[], AnalysisRange] = None):
    """
    Get stock parameters

    Args:
        stock_param (StockParam): StockParam to update.
        anal_rng (AnalysisRange, optional):
                Range entry method. Defaults to AnalysisRange.DATE.
        range_select (Callable[[], AnalysisRange], optional):
                Range entry method select function. Defaults to None.
    """
    if anal_rng == AnalysisRange.ASK:
        anal_rng = range_select()

    stock_param = get_date_range(stock_param) \
        if anal_rng == AnalysisRange.DATE \
        else get_period_range(stock_param)

    return stock_param


def get_stock_param(
        symbol: str = None,
        anal_rng: AnalysisRange = AnalysisRange.DATE,
        range_select: Callable[[], AnalysisRange] = None) -> StockParam:
    """
    Get stock parameters

    Args:
        symbol (str, optional): Stock symbol. Defaults to None.
        anal_rng (AnalysisRange, optional):
                Range entry method. Defaults to AnalysisRange.DATE.
        range_select (Callable[[], AnalysisRange], optional):
                Range entry method select function. Defaults to None.

    Returns:
        StockParam: stock parameters
    """
    stock_param = get_stock_param_symbol(symbol)

    if stock_param is not None:
        get_stock_param_range(stock_param, anal_rng, range_select)

    return stock_param


def analyse_stock(
        data_frame: Union[pd.DataFrame, List[str], StockDownload],
        stock_param: StockParam) -> dict:
    """
    Analyse stock data

    Args:
        data_frame (Union[Pandas.DataFrame, List[str], StockDownload]):
                                                            data to analyse
        stock_param (StockParam): stock parameters

    Returns:
        dict: dict of analysis results, like {
            'from': [date],
            'to': [date],
            'symbol': [str]
            'data_na': {
                'from': {
                    'missing': [bool],
                    'start': [date],
                    'end': [date]
                }
                'to': { ... },
                'Open': (bool),
                ...
                'Volume': (bool)
            }
            'OpenMin': 11.34,
            'OpenMax': 12.34,
            'OpenChange': 1.0,
            'OpenPercentChange': 8.82,
            .....
        }
    """
    if isinstance(data_frame, StockDownload):
        if not data_frame.response_ok:
            return None

        # take analysis info from data class
        analyse = data_frame.data_frame
        from_date = data_frame.stock_param.from_date
        to_date = data_frame.stock_param.to_date
        symbol = data_frame.stock_param.symbol
    else:
        # raw analysis and take date info from data
        analyse = data_frame
        from_date = None
        to_date = None
        symbol = stock_param.symbol
    if isinstance(analyse, list):
        # convert list to data frame
        analyse = StockDownload.list_to_frame(analyse)

    # data in chronological order
    # FutureWarning: Comparison of Timestamp with datetime.date is
    # deprecated
    analyse[DfColumn.DATE.title] = \
        analyse[DfColumn.DATE.title].apply(pd.Timestamp)

    analyse.sort_values(by=DfColumn.DATE.title, ascending=True, inplace=True)
    if not from_date:
        # get date info for raw analysis
        from_date = analyse[DfColumn.DATE.title].min()
        to_date = analyse[DfColumn.DATE.title].max()
    else:
        # filter by min & max dates
        analyse = filter_data_frame_by_date(
                        analyse, from_date, to_date, DfColumn.DATE.title)

    # check if gap between requested and received data
    from_date = convert_date_time(from_date, DateFormat.DATE)
    to_date = convert_date_time(to_date, DateFormat.DATE)

    analysis = {
        'from': from_date,
        'to': to_date,
        'symbol': symbol,
        'data_na': {
            'from': missing_data(stock_param.from_date, from_date),
            'to': missing_data(stock_param.to_date, to_date),
        }
    }

    for column in DfColumn.NUMERIC_COLUMNS:
        data_series = analyse[column.title]

        # min value
        analysis[DfStat.MIN.column_key(column)] = data_series.min()

        # max value
        analysis[DfStat.MAX.column_key(column)] = data_series.max()

        # avg value
        analysis[DfStat.AVG.column_key(column)] = round_price(
                                                        data_series.mean()
                                                    )

        # change
        start_vol = data_series.iat[0]
        change = round_price(start_vol - \
                            data_series.iat[len(data_series)-1])
        analysis[DfStat.CHANGE.column_key(column)] = change

        # percentage change
        analysis[DfStat.PERCENT_CHANGE.column_key(column)] = round(
            (change / (
                start_vol if start_vol != 0 else 1
            )) * 100, PERCENT_PRECISION
        )

        # check for missing data
        analysis['data_na'][column.title] = 0 in data_series.values

    # special case for Volume - int(average volume)
    analysis[DfStat.AVG.column_key(DfColumn.VOLUME)] = int(
        analysis[DfStat.AVG.column_key(DfColumn.VOLUME)]
    )

    return analysis


def round_price(price: float) -> float:
    """
    Round a stock price

    Args:
        price (float): stock price

    Returns:
        float: rounded value
    """
    return round(price, PRICE_PRECISION)


def missing_data(req_date: date, recv_date: date):
    """
    Generate a missing data object

    Args:
        req_date (date): requested date
        recv_date (date): received date

    Returns:
        object: object of form {
            'missing': (bool),
            'start': (date),
            'end': (date)
        }
    """
    data_delta = convert_date_time(recv_date, DateFormat.DATE) - \
                    convert_date_time(req_date, DateFormat.DATE)
    return {
        # mark greater than a weekend as missing data
        'missing': data_delta.days > 2,
        'start': req_date,
        'end': recv_date - timedelta(days=1)
    }
