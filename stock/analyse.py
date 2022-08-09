"""
Stock analysis related functions
"""
from copy import copy
from datetime import date, datetime, timedelta
import re
from typing import Callable, List, Tuple, Union
from collections import namedtuple

import pandas as pd

from utils import (
    get_input, error, ABORT, HELP, last_day_of_month, FRIENDLY_DATE_FMT,
    filter_data_frame_by_date, convert_date_time, DateFormat, pick_menu
)
from .data import StockDownload, StockParam
from .enums import DfColumn, DfStat, AnalysisRange


DATE_SEP = '-'
SLASH_SEP = '/'
DOT_SEP = '.'
SPACE_SEP = ' '
FROM = 'from'
TO = 'to'
YTD = 'ytd'
PREPS = [FROM, TO]
PREPS_YTD = copy(PREPS)
PREPS_YTD.extend([YTD])

DATE_FORM = f'dd{DATE_SEP}mm{DATE_SEP}yyyy'
DATE_FORMAT = f'%d{DATE_SEP}%m{DATE_SEP}%Y'
DATE_FMT = '{day}'+DATE_SEP+'{mth}'+DATE_SEP+'{year}'

MIN_DATE = datetime(1962, 2, 1)

FROM_DATE_HELP = f"Enter analysis start date, or '{ABORT}' to cancel"
TO_DATE_HELP = f"Enter analysis end date (excluded from analysis), "\
               f"or '{ABORT}' to cancel"

PERIOD_TYPES = f"   - '[period] [{FROM}|{TO}] [{DATE_FORM}]'\n"\
              f"   - '[{DATE_FORM}] [{FROM}|{TO}] [{DATE_FORM}]'\n"\
              f"   - '{YTD} [{DATE_FORM}]'\n"
PERIOD_HELP = f"Enter period in either of the following forms:\n"\
              f"{PERIOD_TYPES}"\
              f"or enter '{ABORT}' to cancel.\n"\
              f"where: [period]      - is of the form '[0-9][d|w|m|y]' "\
                f"with 'd' for day,\n"\
              f"                       'w' for week, 'm' for month and "\
                f"'y' for year.\n"\
              f"                       e.g. '5d' is 5 days\n"\
              f"       [{FROM}|{TO}|ytd] - '{FROM}'/'{TO}' date or "\
                f"'year-to-date' date.\n"\
              f"                       Note: [period] not required for "\
                f"'{YTD}'.\n"\
              f"                       e.g. '{YTD} "\
                f"{datetime.now().strftime(DATE_FORMAT)}'\n" \
              f"       [{DATE_FORM}]  - date, or today if omitted\n"\
              f"                       month names may be used"
PERIOD_ERROR = f"Invalid period, enter like\n"\
              f"{PERIOD_TYPES}"\
              f"or '{HELP}' for more information."


# TODO add more entry methods, abbreviated month etc. and
# suggestions for incorrect input(?)
# date forms:
# 1st jan 2022

MONTHS = {
    1: ['jan', 'january'],
    2: ['feb', 'february'],
    3: ['mar', 'march'],
    4: ['apr', 'april'],
    5: ['may'],
    6: ['jun', 'june'],
    7: ['jul', 'july'],
    8: ['aug', 'august'],
    9: ['sep', 'september', 'sept'],
    10: ['oct', 'october'],
    11: ['nov', 'november'],
    12: ['dec', 'december'],
}

SEP_REGEX = rf'[{DATE_SEP}{SLASH_SEP}{DOT_SEP}{SPACE_SEP}]'
DMY_REGEX = rf"(\d+){SEP_REGEX}{{1}}(\d+){SEP_REGEX}{{0,1}}(\d*)"
DMY_TEXT_REGEX = rf"(\d+){SEP_REGEX}{{1}}([a-zA-Z]+){SEP_REGEX}{{0,1}}(\d*)"
MY_REGEX = rf"(\d+){SEP_REGEX}{{1}}(\d+)"
MY_TEXT_REGEX = rf"([a-zA-Z]+){SEP_REGEX}{{1}}(\d*)"
PERIOD_REGEX = r"(\d+)\s*([dwmy])"
DMY_MY_KEY = re.compile(r'd?my-d?my')
REGEX = {
    'period-now': re.compile(rf"^\s*{PERIOD_REGEX}\s+(\w+)\s*$"),
    'ytd-dmy': re.compile(rf"^\s*(\w+)\s+{DMY_REGEX}\s*$"),
    'ytd-dmy-text': re.compile(rf"^\s*(\w+)\s+{DMY_TEXT_REGEX}\s*$"),
    'ytd-now': re.compile(r"^\s*(\w+)\s*$")
}
# TODO revisit period pattern identification
# probably better to identify individual elements and check
# they don't overlap and are in correct order
for dmy1 in ['dmy', 'my']:
    dmy1_regex = DMY_REGEX if dmy1 == 'dmy' else MY_REGEX
    dmy1_text_regex = DMY_TEXT_REGEX if dmy1 == 'dmy' else MY_TEXT_REGEX

    REGEX[f'{dmy1}-period'] = \
        re.compile(rf"^\s*{PERIOD_REGEX}\s+(\w+)\s+{dmy1_regex}\s*$")
    REGEX[f'{dmy1}-period-text'] = \
        re.compile(rf"^\s*{PERIOD_REGEX}\s+(\w+)\s+{dmy1_text_regex}\s*$")

    for dmy2 in ['dmy', 'my']:
        dmy2_regex = DMY_REGEX if dmy2 == 'dmy' else MY_REGEX
        dmy2_text_regex = DMY_TEXT_REGEX if dmy2 == 'dmy' else MY_TEXT_REGEX

        REGEX[f'{dmy1}-{dmy2}'] = \
            re.compile(rf"^\s*{dmy1_regex}\s+(\w+)\s+{dmy2_regex}\s*$")
        REGEX[f'{dmy1}-{dmy2}-text'] = \
            re.compile(
                rf"^\s*{dmy1_text_regex}\s+(\w+)\s+{dmy2_text_regex}\s*$")

PERIOD_KEYS = [
            'num',          # (int): unit count
            'time_unit',    # (str): time unit; d/m/y
            'time_dir',     # (str): direction; from/to
            'day',          # (int): day
            'month',        # (int): month
            'year'          # (int): year
        ]
""" Period param object keys as per DMY_REGEX """
DIR_KEY_IDX = PERIOD_KEYS.index('time_dir')
DAY_KEY_IDX = PERIOD_KEYS.index('day')
MTH_KEY_IDX = PERIOD_KEYS.index('month')
YR_KEY_IDX = PERIOD_KEYS.index('year')

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
    Decorator to validate a date and ensure passes ``check``
    against the specified date

    Args:
        limit_datetime (datetime): date to pass check of
        check (str): error check to perform; '<', '<=', '==', '>=' or '>'

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
        is_error = False
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


def validate_period(period_str: str) -> Union[Period, None]:
    """
    Validate a period string

    Args:
        period_str (str): input period string

    Returns:
        Union[Period, None]: string object if valid, otherwise None
    """
    period = None
    hit_and_miss = False
    period_str = period_str.strip().lower()

    for regex_key, regex in REGEX.items():
        match = regex.match(period_str)
        if match:
            params = period_param_template()

            if DMY_MY_KEY.match(regex_key):
                # check formats using combinations of
                # 'dd-mm-yyyy', 'dd-MMM-yyyy', 'dd-mm', 'dd-MMM',
                # 'mm-yyyy' and 'MMM-yyyy'
                # in '<from> to <to>'

                # search for 'from'/'to'
                from_to_idx = -1
                for idx, group in enumerate(match.groups()):
                    if group in PREPS:
                        # individual groups in match start at 1
                        # should be 3 or 4, i.e.
                        # d:1 m:2 y:3 *to:4* m:5 y:6 or
                        # m:1 y:2 *to:3* d:4 m:5 y:6
                        from_to_idx = idx + 1
                        break

                params2 = None
                if 3 <= from_to_idx <= 4:
                    params2 = period_param_template()
                    len_groups = len(match.groups())
                    if len_groups == 7:
                        # dmy-dmy match
                        # day/mth/year period keys at end,
                        # follow regex group order of DMY_DMY_REGEX
                        # d:1 m:2 y:3 to:4 d:5 m:6 y:7
                        for step, prd_prm in enumerate([params, params2]):
                            groups_to_params(
                                match, DAY_KEY_IDX,
                                # dmy + preposition i.e. 4
                                (step * (len(PERIOD_KEYS) - DAY_KEY_IDX + 1)),
                                prd_prm)

                    elif len_groups == 6:
                        # index of 'from'/'to' determines if my-dmy or dmy-my
                        # d:1 m:2 y:3 to:4 m:5 y:6 or m:1 y:2 to:3 d:4 m:5 y:6
                        groups_to_params(
                            match,
                            DAY_KEY_IDX if from_to_idx == 4 else MTH_KEY_IDX,
                            0, params)
                        groups_to_params(
                            match,
                            MTH_KEY_IDX if from_to_idx == 4 else DAY_KEY_IDX,
                            # (dmy or my) + preposition i.e. 4 or 3
                            4 if from_to_idx == 4 else 3, params2)

                    elif len_groups == 5:
                        # my-my
                        for step, prd_prm in enumerate([params, params2]):
                            groups_to_params(
                                match, MTH_KEY_IDX,
                                # my + preposition i.e. 3
                                (step * (len(PERIOD_KEYS) - MTH_KEY_IDX + 1)),
                                prd_prm)

                # else have no 'from'/'to' so can't be valid

                if params2:
                    for step, prd_prm in enumerate([params, params2]):
                        sanitise_params(prd_prm, 'text' in regex_key)

                    period = get_dmy_dmy_period(
                                params, match.group(from_to_idx), params2)
                    hit_and_miss = period is None

                params = None
            elif regex_key.startswith('dmy'):
                # check formats like '1d from dd-mm-yyyy'
                # or '1d from dd-MMM'

                # period keys follows regex group order of DMY_REGEX
                for idx, key in enumerate(PERIOD_KEYS):
                    params[key] = match.group(idx + 1)
            elif regex_key == 'period-now':
                # check formats with omitted date like '1d from'
                # period keys follows regex group order of DMY_NOW_REGEX
                # excluding day/mth/year at end
                for idx, key in enumerate(PERIOD_KEYS):
                    if idx < DAY_KEY_IDX:
                        params[key] = match.group(idx + 1)
            elif regex_key.startswith('ytd-dmy'):
                # check formats like 'ytd dd-mm-yyyy'
                # or 'ytd dd-MMM'

                # dir/day/mth/year period keys at end,
                # follow regex group order of YTD_REGEX
                for idx in range(DIR_KEY_IDX, len(PERIOD_KEYS)):
                    params[PERIOD_KEYS[idx]] =\
                        match.group(idx - DIR_KEY_IDX + 1)
            elif regex_key == 'ytd-now':
                # check formats with omitted date like 'ytd'
                # dir/day/mth/year period keys at end,
                # follow regex group order of YTD_REGEX
                params[PERIOD_KEYS[DIR_KEY_IDX]] = match.group(1)

            if params is not None:
                sanitise_params(params, 'text' in regex_key)

                period = make_dmy_period(params)

            if period or hit_and_miss:
                # have period or attempted match invalid, all done
                break
    else:
        error(PERIOD_ERROR)

    return period


def groups_to_params(
        match: object, start_idx: int, offset: int, params: dict = None):
    """
    Copy match groups to params dict

    Args:
        match (object): match object
        start_idx (int): start index of PERIOD_KEYS
        offset (int): offset in match object groups
        params (dict, optional): params object. Defaults to None.

    Returns:
        dict: params object
    """
    if params is None:
        params = period_param_template()

    for idx in range(start_idx, len(PERIOD_KEYS)):
        key = PERIOD_KEYS[idx]
        group = (idx - start_idx + 1) + offset
        params[key] = match.group(group)
    return params


def period_param_template() -> dict:
    """ Generate period parameter object template """
    return {key: None for key in PERIOD_KEYS}


def param_date(params: dict) -> Tuple[int, int, int]:
    """
    Unpack date elements from ``param``

    Args:
        params (dict): object of the form generated by
                         period_param_template()

    Returns:
        Tuple[int, int, int]: day, month, year
    """
    # default to today's date
    today = datetime.now()
    day = int(params['day']) if params['day'] else today.day
    month = int(params['month']) if params['month'] else today.month
    year = int(params['year']) if params['year'] else today.year
    if year < 100:
        # 2 digit year, assume this century
        year += (int(today.year / 100) * 100)
    return day, month, year


def sanitise_params(params: dict, do_mth_text: bool):
    """
    Convert month strings to number in a params object

    Args:
        params (dict): params object
        do_mth_text (bool): do month test conversion flag
    """
    if params['year'] is None and params['month'] is None \
            and params['day'] is None:
        # nothing to do
        return

    def set_mth_yr():
        params['year'] = params['month']
        params['month'] = params['day']
        params['day'] = 1

    if params['year'] is None or len(params['year']) == 0:
        # no year, so check for no day
        mth_len = len(params['month'])

        if mth_len == 4:
            # 1st of month date
            set_mth_yr()

        elif mth_len == 2 and params['month'].isnumeric() \
                and params['day'].isnumeric():
            # ambiguous, mth-year or day-mth

            if int(params['month']) > 12:
                # must be year
                set_mth_yr()
            elif int(params['day']) <= 12:
                century = int(datetime.now().year / 100) * 100

                year = int(params['month']) + century
                while year > datetime.now().year:
                    year -= 1000

                mth_yr = datetime(
                        year=year,
                        month=int(params['day']),
                        day=1)
                day_mth = datetime(
                        year=datetime.now().year,
                        month=int(params['month']),
                        day=int(params['day']))

                choice = pick_menu([
                    (mth_yr.strftime(FRIENDLY_DATE_FMT), mth_yr),
                    (day_mth.strftime(FRIENDLY_DATE_FMT), day_mth)
                ], menu_title='Ambiguous date, which did you mean?')

                params['year'] = choice.year
                params['month'] = choice.month
                params['day'] = choice.day

    have_flags = 0
    for idx in range(DAY_KEY_IDX, len(PERIOD_KEYS)):
        if params[PERIOD_KEYS[idx]] is None:
            params[PERIOD_KEYS[idx]] = ''
        else:
            have_flags |= (1 << idx)

    if have_flags == (1 << MTH_KEY_IDX) + (1 << YR_KEY_IDX):
        # default 1st of month when have mth & yr
        params[PERIOD_KEYS[DAY_KEY_IDX]] = 1

    if do_mth_text and not params['month'].isnumeric():
        param_mth = params['month'].lower()
        for mth, mth_strs in MONTHS.items():
            found = False
            for mth_str in mth_strs:
                if param_mth == mth_str:
                    params['month'] = mth
                    found = True
                    break
            if found:
                break


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
    valid = params['time_dir'] in PREPS_YTD
    if valid:

        is_fwd = params['time_dir'] == FROM
        num = (int(params['num'])
               if params['num'] else 0) * (1 if is_fwd else -1)
        time_unit = params['time_unit']
        # default to today's date
        day, month, year = param_date(params)

        out_date = None
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
                    not_new_year = not_december  # no new year if not december
                else:
                    step = -1   # step back to
                    not_new_year = not_january  # no new year if not january

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
                        if in_date.day > new_mth_last_day else in_date.day

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

            if valid and out_date is not None:
                period = Period(in_date, out_date) \
                            if is_fwd else Period(out_date, in_date)
                valid = period.from_date < period.to_date \
                    and period.to_date.date() <= datetime.now().date()
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

    if in_date and out_date and preposition in PREPS:
        if validate_date_limit(
                in_date,
                # error condition check
                GT if preposition == TO else LT)(
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


def analyse_stock(
        data_frame: Union[pd.DataFrame, List[str], StockDownload],
        stock_param: StockParam) -> Union[dict, None]:
    """
    Analyse stock data

    Args:
        data_frame (Union[Pandas.DataFrame, List[str], StockDownload]):
                                                            data to analyse
        stock_param (StockParam): stock parameters

    Returns:
        dict: None if error, or dict of analysis results, like {
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
        analysis[DfStat.AVG.column_key(column)] = \
            round_price(data_series.mean())

        # change
        start_vol = data_series.iat[0]
        change = round_price(
            start_vol - data_series.iat[len(data_series)-1])
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
    data_delta = convert_date_time(
        recv_date,
        DateFormat.DATE) - convert_date_time(req_date, DateFormat.DATE)
    return {
        # mark greater than a weekend as missing data
        'missing': data_delta.days > 2,
        'start': req_date,
        'end': recv_date - timedelta(days=1)
    }
