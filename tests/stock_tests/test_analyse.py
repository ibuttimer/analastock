"""
Unit tests for stock analyse functions
"""
from datetime import datetime, timedelta, time
from typing import Callable
import unittest
from collections import namedtuple
from stock import standardise_stock_param, StockParam
from stock.analyse import (
    DATE_FORMAT, DATE_SEP, DOT_SEP, SLASH_SEP, validate_period, MONTHS
)


Param = namedtuple("Param", ['test_date', 'from_ans', 'to_ans', 'step'])

# separators
SEP_LIST = [DATE_SEP, SLASH_SEP, DOT_SEP]

class TestAnalyse(unittest.TestCase):
    """
    Units tests for analyse functions
    """

    def test_from_1st_of_month(self):
        """
        Test standardise_stock_param for 1st of month from_date
        """
        first_feb = datetime(year=2022, month=2, day=1)
        stock_param = standardise_stock_param(
            StockParam.stock_param_of(
                'test',
                first_feb.replace(day=2),
                first_feb.replace(day=10)
            )
        )
        self.assertEqual(stock_param.from_date, first_feb.date())
        self.assertEqual(stock_param.from_datetime, first_feb)


    def test_to_1st_of_month(self):
        """
        Test standardise_stock_param for 1st of month to_date
        """
        first_feb = datetime(year=2022, month=2, day=1)
        first_mar = datetime(year=2022, month=3, day=1)
        stock_param = standardise_stock_param(
            StockParam.stock_param_of(
                'test',
                first_feb,
                first_feb.replace(day=10)
            )
        )
        self.assertEqual(stock_param.to_date, first_mar.date())
        self.assertEqual(stock_param.to_datetime, first_mar)


    def test_to_1st_of_jan(self):
        """
        Test standardise_stock_param for 1st of month to_date
        """
        first_dec = datetime(year=2021, month=12, day=1)
        first_jan = datetime(year=2022, month=1, day=1)
        stock_param = standardise_stock_param(
            StockParam.stock_param_of(
                'test',
                first_dec,
                first_dec.replace(day=10)
            )
        )
        self.assertEqual(stock_param.to_date, first_jan.date())
        self.assertEqual(stock_param.to_datetime, first_jan)


    def test_period_dmy(self):
        """
        Test period validation for day/month/year
        """
        self.period_dmy_simple(lambda test_date, is_last_test : DATE_FORMAT)
        self.period_dmy_days(lambda test_date, is_last_test : DATE_FORMAT)
        self.period_dmy_months(lambda test_date, is_last_test : DATE_FORMAT)

        # no future dates omitted date
        self.assertIsNone(validate_period('1d from'))

        # no future dates omitted date
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        yesterday = datetime.combine(yesterday, time.min)
        today = datetime.combine(today, time.min)
        period = validate_period('1d to')
        self.assertEqual(period.from_date, yesterday)
        self.assertEqual(period.to_date, today)


    def test_period_dmy_text(self):
        """
        Test period validation for day/month/year with month text
        """
        test_state = self.mth_text_state()

        def mth_text(test_date: datetime, is_last_test: bool):
            return self.mth_text(test_date, is_last_test, test_state)

        # do tests
        while test_state['in_progress']:
            self.period_dmy_simple(mth_text)

        while test_state['in_progress']:
            self.period_dmy_days(mth_text)

        while test_state['in_progress']:
            self.period_dmy_months(mth_text)


    def period_dmy_simple(
            self, from_fmt: Callable[[datetime], str], track: str = None):
        """
        Test period validation of day/month/year with no
        month boundaries conditions

        Args:
            from_fmt (Callable[[datetime], str]):
                    function to return format of test date
            track (str): test tracking
        """
        units = {
            'd': 'day',
            'w': 'week',
            'm': 'month',
            'y': 'year'
        }
        track = f' trk={track} ' if track else ''

        # NB: don't use future test dates

        unit_count = 2
        test_from = datetime(2019, 6, 15)
        self.assertLess(test_from, datetime.now())

        # simple test, no month boundaries conditions
        for idx, unit in enumerate(units.keys()):
            for sep_idx, sep in enumerate(SEP_LIST):
                is_last_test = idx == len(units.keys()) - 1 \
                                    and sep_idx == len(SEP_LIST) - 1
                fmt = from_fmt(test_from, is_last_test).replace(DATE_SEP, sep)

                date_str = test_from.strftime(fmt)

                for time_dir in ['from', 'to']:
                    is_from = time_dir == 'from'

                    base_val = test_from.year if unit == 'y' else \
                                test_from.month if unit == 'm' else \
                                    test_from.day
                    if unit == 'w':
                        # convert week to 7 days
                        key = 'd'
                        multiplier = 7
                    else:
                        key = unit
                        multiplier = 1
                    update = {
                        f'{units[key]}':
                            base_val + (
                                (unit_count if is_from else -unit_count)
                                    * multiplier
                            )
                    }

                    period_str = f'{unit_count}{unit} {time_dir} {date_str}'

                    # don't test 2 number years, covered in dmy_dmy_from_to()

                    self.padding_check(period_str,
                            test_from if is_from else \
                                test_from.replace(**update),
                            test_from.replace(**update) if is_from else \
                                test_from,
                            True, desc=f'no month boundaries {track}')


    def period_dmy_days(
            self, from_fmt: Callable[[datetime], str], track: str = None):
        """
        Test period validation for day/month/year for day boundaries

        Args:
            from_fmt (Callable[[datetime], str]):
                    function to return format of test date
            track (str): test tracking
        """
        track = f' trk={track} ' if track else ''
        days_to_test = [
            datetime(2022, 1, 1), datetime(2021, 12, 31),   # end of year
            datetime(2020, 2, 28), datetime(2022, 2, 28),   # leap/non-leap
            datetime(2021, 9, 30), datetime(2021, 8, 31)
        ]

        # day boundaries
        unit_count = 1
        for idx, test_from in enumerate(days_to_test):
            for sep_idx, sep in enumerate(SEP_LIST):
                is_last_test = idx == len(days_to_test) - 1 \
                                    and sep_idx == len(SEP_LIST) - 1
                fmt = from_fmt(test_from, is_last_test).replace(DATE_SEP, sep)
                date_str = test_from.strftime(fmt)

                delta = timedelta(days=unit_count)
                for time_dir in ['from', 'to']:
                    is_from = time_dir == 'from'

                    period_str = f'{unit_count}d {time_dir} {date_str}'
                    self.padding_check(period_str,
                            test_from if is_from else test_from - delta,
                            test_from + delta if is_from else test_from,
                            True,
                            desc=f'month boundaries {track} idx={idx}')


    def period_dmy_months(
            self, from_fmt: Callable[[datetime], str], track: str = None):
        """
        Test period validation for day/month/year for month boundaries

        Args:
            from_fmt (Callable[[datetime], str]): 
                    function to return format of test date
            track (str): test tracking
        """
        test_params = [
            #       test_date, date for from period, date for to period
            # end of year
            Param(datetime(2022, 1, 1), datetime(2022, 2, 1),
                datetime(2021, 12, 1), 1),
            Param(datetime(2021, 12, 31), datetime(2022, 1, 31),
                datetime(2021, 11, 30), 1),
            # leap year
            Param(datetime(2020, 2, 28), datetime(2020, 3, 28),
                datetime(2020, 1, 28), 1),
            # non-leap year
            Param(datetime(2022, 2, 28), datetime(2022, 3, 31),
                datetime(2022, 1, 31), 1),
            # end of month
            Param(datetime(2021, 9, 29), datetime(2021, 10, 29),
                datetime(2021, 8, 29), 1),
            Param(datetime(2021, 9, 30), datetime(2021, 10, 31),
                datetime(2021, 8, 31), 1),
            Param(datetime(2021, 9, 30), datetime(2021, 11, 30),
                datetime(2021, 7, 31), 2),
            # need 2 months gap to test 31th; mar-may-jul or aug-sep-dec
            Param(datetime(2021, 5, 31), datetime(2021, 7, 31),
                datetime(2021, 3, 31), 2)
        ]
        for idx, param in enumerate(test_params):
            #  1   2   3   4   5   6   7   8   9  10  11  12
            #[31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
            for sep_idx, sep in enumerate(SEP_LIST):
                is_last_test = idx == len(test_params) - 1 \
                                    and sep_idx == len(SEP_LIST) - 1
                fmt = from_fmt(param.test_date, is_last_test)\
                        .replace(DATE_SEP, sep)
                date_str = param.test_date.strftime(fmt)

                for time_dir in ['from', 'to']:
                    is_from = time_dir == 'from'

                    period_str = f'{param.step}m {time_dir} {date_str}'
                    self.padding_check(period_str,
                            param.test_date if is_from else \
                                param.to_ans,
                            param.from_ans if is_from else \
                                param.test_date,
                            True,
                            desc=f'month boundaries {track} idx={idx}')


    def test_period_ytd(self):
        """
        Test period validation for ytd
        """
        self.period_ytd_test(lambda test_date, is_last_test : DATE_FORMAT)


    def test_period_ytd_text(self):
        """
        Test period validation for ytd with month text
        """
        test_state = self.mth_text_state()

        def mth_text(test_date: datetime, is_last_test: bool):
            return self.mth_text(test_date, is_last_test, test_state)

        # do tests
        while test_state['in_progress']:
            self.period_ytd_test(mth_text)


    def period_ytd_test(self, from_fmt: Callable[[datetime], str]):
        """
        Test period validation for ytd
        """
        # NB: don't use future test dates

        # ytd tests
        test_date = datetime(2022, 2, 1)
        for sep_idx, sep in enumerate(SEP_LIST):
            is_last_test = sep_idx == len(SEP_LIST) - 1
            fmt = from_fmt(test_date, is_last_test)\
                    .replace(DATE_SEP, sep)

            period_str = f'ytd {test_date.strftime(fmt)}'

            self.padding_check(period_str, test_date.replace(month=1, day=1),
                               test_date, True)

            # no zero time period
            zero_date = datetime.now().replace(month=1, day=1)
            self.assertIsNone(
                validate_period(f'ytd {zero_date.strftime(fmt)}')
            )


    @unittest.skipIf(datetime.now().month == 1 and datetime.now().day == 1,
                        "'can't test omitted ytd on 1st January")
    def test_period_ytd_omitted(self):
        """
        Test period validation for ytd with omitted date
        """
        # ytd omitted date
        jan1 = datetime.combine(
            datetime.now().replace(month=1, day=1).date(), time.min)
        today = datetime.combine(datetime.now().date(), time.min)
        period_str = 'ytd'
        self.padding_check(period_str, jan1, today, True)


    def test_period_dmy_dmy(self):
        """
        Test period validation for dmy to dmy
        """
        # dmy [to/from] dmy tests
        test_yr = 2022
        for idx, param in enumerate([
                    (datetime(test_yr, 2, 1), datetime(test_yr, 3, 1), 'to'),
                    (datetime(test_yr, 3, 1), datetime(test_yr, 2, 1), 'from')
                ]):
            test_from, test_to, valid_dir = param
            # NB: convenient method of debugging is set a conditional
            #     break on 'track == "track msg for error"'
            track = f'idx:{idx}'

            self.dmy_dmy_from_to(
                test_from, DATE_FORMAT, test_to, DATE_FORMAT,
                test_yr, valid_dir, track)


    def test_period_dmy_dmy_text(self):
        """
        Test period validation for dmy to dmy with text months
        """
        # dmy [to/from] dmy tests
        # use last year to avoid future date errors
        test_yr = datetime.now().year - 1
        for mth, mth_strs in MONTHS.items():

            months = []
            if 0 < mth < 12:
                months.append(
                    (datetime(test_yr, mth, 1),
                        datetime(test_yr, mth + 1, 1), 'to')
                )
            if 1 < mth < 12:
                months.append(
                    (datetime(test_yr, mth + 1, 1),
                        datetime(test_yr, mth, 1), 'from')
                )

            for mth_idx, _ in enumerate(mth_strs):

                for idx, param in enumerate(months):
                    # NB: convenient method of debugging is set a conditional
                    #     break on 'track == "track msg for error"'
                    track = f'mth:{mth} mth_idx:{mth_idx} idx:{idx}'

                    test_from, test_to, valid_dir = param

                    from_mth = self.get_month_text(test_from, mth_idx)\
                                    .capitalize()
                    to_mth = self.get_month_text(test_to, mth_idx)\
                                    .upper()

                    # Month as text
                    self.dmy_dmy_from_to(
                        test_from,
                        DATE_FORMAT.replace('%m', from_mth),
                        test_to,
                        DATE_FORMAT.replace('%m', to_mth),
                        test_yr, valid_dir, track)


    def dmy_dmy_from_to(self,
            test_from: datetime, from_fmt: str,
            test_to: datetime, to_fmt: str,
            test_yr: int, valid_dir: str, track: str,
            do_day_mth: bool = True):
        """
        Perform day-month-year/day-month-year testing

        Args:
            test_from (datetime): from date
            from_fmt (str): format of from date
            test_to (datetime): to date
            to_fmt (str): format of to date
            test_yr (int): test year
            valid_dir (str): valid direction; 'from' or 'to'
            track (str): test tracking
            do_day_mth (bool, optional): do day-month tests. Defaults to True.
        """
        for sep in SEP_LIST:
            # day-month-year
            from_fmt_dmy = from_fmt.replace(DATE_SEP, sep)
            to_fmt_dmy = to_fmt.replace(DATE_SEP, sep)

            for time_dir in ['from', 'to']:
                period_str = f'{test_from.strftime(from_fmt_dmy)} '\
                            f'{time_dir} '\
                            f'{test_to.strftime(to_fmt_dmy)}'

                # test 2 number years
                for year in [str(test_yr), str(int(test_yr % 100))]:
                    period_str = period_str.replace(str(test_yr), year)

                    self.padding_check(
                        period_str, test_from, test_to,
                        time_dir == valid_dir,
                        desc=f'year len {len(year)} trk={track}')

            # day-month
            if do_day_mth and test_yr == datetime.now().year:
                from_fmt_dm = from_fmt_dmy[0:from_fmt_dmy.index(f'{sep}%Y')]
                to_fmt_dm = to_fmt_dmy[0:to_fmt_dmy.index(f'{sep}%Y')]

                for time_dir in ['from', 'to']:
                    period_str = f'{test_from.strftime(from_fmt_dm)} '\
                                f'{time_dir} '\
                                f'{test_to.strftime(to_fmt_dm)}'

                    self.padding_check(
                        period_str, test_from, test_to,
                        time_dir == valid_dir,
                        desc=f'day-month trk={track}')


    def padding_check(
                self, period_str: str, test_from: datetime, test_to: datetime,
                is_valid: bool, desc: str = None):
        """
        Do period string padding and extra text tests

        Args:
            period_str (str): period string
            test_from (datetime): expected from date
            test_to (datetime): expected to date
            is_valid (bool): expect a valid result
            desc (str, optional): description. Defaults to None.
        """
        for padding_cmt, padding in [('no padding', ''), ('padding', ' ')]:
            with self.subTest(msg=f'{period_str} '\
                                  f'{f"{desc} " if desc else ""}'\
                                  f'{padding_cmt}'):

                period = validate_period(
                    f'{padding}{period_str}{padding}')
                if is_valid:
                    self.assertIsNotNone(period)
                    self.assertEqual(period.from_date, test_from)
                    self.assertEqual(period.to_date, test_to)
                else:
                    self.assertIsNone(period)

        with self.subTest(msg=f'{period_str} trailing text'):

            period = validate_period(f'{period_str} xyz')
            self.assertIsNone(period)


    def get_month_text(self, test_date: datetime, mth_idx: int) -> str:
        """
        Get the month text for the specified date and index

        Args:
            test_date (datetime): date
            mth_idx (int): index of month test to get

        Returns:
            str: month text
        """
        return MONTHS[test_date.month][
                mth_idx % len(MONTHS[test_date.month])
            ]


    def mth_text(
                self, test_date: datetime, is_last_test: bool,
                state: dict) -> str:
        """
        Get the month test for the specified date

        Args:
            test_date (datetime): date
            is_last_test (bool): current call in last call
            state (dict): state dict with {
                'testing_date': [datetime: date currently being tested]
                'mth_idx': [int: index of month text]
                'max_idx': [int: max index of month text]
                'in_progress': [bool: test in progress]
            }

        Returns:
            str: date format
        """
        state['in_progress'] = not is_last_test

        if state['testing_date'] is None:
            state['started'] = True
            state['mth_idx'] = 0
            state['max_idx'] = len(MONTHS[test_date.month])
        else:
            state['mth_idx'] += 1
            if state['mth_idx'] == state['mth_idx'] - 1:
                state['testing_date'] = None

        return DATE_FORMAT.replace(
                '%m', self.get_month_text(test_date, state['mth_idx']))


    def mth_text_state(self):
        """
        Get a month test for the specified date state object

        Returns:
            dict: state dict with {
                'testing_date': [datetime: date currently being tested]
                'mth_idx': [int: index of month text]
                'max_idx': [int: max index of month text]
                'in_progress': [bool: test in progress]
            }
        """
        return {
            key: None for key in [
                'testing_date', 'mth_idx', 'max_idx', 'in_progress']
        }


if __name__ == '__main__':
    unittest.main()
