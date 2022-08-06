"""
Unit tests for stock analyse functions
"""
from datetime import datetime, timedelta, time
import unittest
from collections import namedtuple
from stock import standardise_stock_param, StockParam
from stock.analyse import (
    DATE_FORMAT, DATE_SEP, DOT_SEP, SLASH_SEP, validate_period
)


Param = namedtuple("Param", ['test_date', 'from_ans', 'to_ans', 'step'])


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
        units = {
            'd': 'day',
            'w': 'week',
            'm': 'month',
            'y': 'year'
        }

        # NB: don't use future test dates

        unit_count = 2
        param = datetime(2019, 6, 15)
        # simple test, no month boundaries conditions
        for unit in ['d', 'w', 'm', 'y']:
            for sep in [DATE_SEP, SLASH_SEP, DOT_SEP]:
                fmt = DATE_FORMAT.replace(DATE_SEP, sep)
                date_str = param.strftime(fmt)

                for time_dir in ['from', 'to']:
                    is_from = time_dir == 'from'

                    base_val = param.year if unit == 'y' else \
                                param.month if unit == 'm' else param.day
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

                    self.padding_check(period_str,
                            param if is_from else param.replace(**update),
                            param.replace(**update) if is_from else param,
                            True, desc='no month boundaries conditions')

        # day boundaries
        unit_count = 1
        for idx, param in enumerate([
            datetime(2022, 1, 1), datetime(2021, 12, 31),   # end of year
            datetime(2020, 2, 28), datetime(2022, 2, 28),   # leap/non-leap
            datetime(2021, 9, 30), datetime(2021, 8, 31)
        ]):
            for sep in [DATE_SEP, SLASH_SEP, DOT_SEP]:
                fmt = DATE_FORMAT.replace(DATE_SEP, sep)
                date_str = param.strftime(fmt)

                delta = timedelta(days=unit_count)
                for time_dir in ['from', 'to']:
                    is_from = time_dir == 'from'

                    period_str = f'{unit_count}d {time_dir} {date_str}'
                    self.padding_check(period_str,
                            param if is_from else param - delta,
                            param + delta if is_from else param,
                            True, desc=f'month boundaries idx={idx}')

        # month boundaries
        for idx, param in enumerate([
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
        ]):
            #  1   2   3   4   5   6   7   8   9  10  11  12
            #[31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
            for sep in [DATE_SEP, SLASH_SEP, DOT_SEP]:
                fmt = DATE_FORMAT.replace(DATE_SEP, sep)
                date_str = param.test_date.strftime(fmt)

                for time_dir in ['from', 'to']:
                    is_from = time_dir == 'from'

                    period_str = f'{param.step}m {time_dir} {date_str}'
                    self.padding_check(period_str,
                            param.test_date if is_from else \
                                param.to_ans,
                            param.from_ans if is_from else \
                                param.test_date,
                            True, desc=f'month boundaries idx={idx}')

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


    def test_period_ytd(self):
        """
        Test period validation for ytd
        """
        # NB: don't use future test dates

        # ytd tests
        test_date = datetime(2022, 2, 1)
        for sep in [DATE_SEP, SLASH_SEP, DOT_SEP]:
            fmt = DATE_FORMAT.replace(DATE_SEP, sep)

            period_str = f'ytd {test_date.strftime(fmt)}'

            self.padding_check(period_str, test_date.replace(month=1, day=1),
                               test_date, True)

        # no zero time period
        test_date = datetime.now().replace(month=1, day=1)
        self.assertIsNone(
            validate_period(f'ytd {test_date.strftime(DATE_FORMAT)}')
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

            for sep in [DATE_SEP, SLASH_SEP, DOT_SEP]:
                # day-month-year
                fmt = DATE_FORMAT.replace(DATE_SEP, sep)

                for time_dir in ['from', 'to']:
                    period_str = f'{test_from.strftime(fmt)} {time_dir} '\
                                f'{test_to.strftime(fmt)}'

                    for year in [str(test_yr), str(int(test_yr % 100))]:
                        period_str = period_str.replace(str(test_yr), year)

                        self.padding_check(
                            period_str, test_from, test_to,
                            time_dir == valid_dir,
                            desc=f'year len {len(year)} idx={idx}')

                # day-month
                fmt = DATE_FORMAT[
                    0:DATE_FORMAT.index(f'{DATE_SEP}%Y')
                ].replace(DATE_SEP, sep)

                for time_dir in ['from', 'to']:
                    period_str = f'{test_from.strftime(fmt)} {time_dir} '\
                                f'{test_to.strftime(fmt)}'

                    self.padding_check(
                        period_str, test_from, test_to,
                        time_dir == valid_dir,
                        desc=f'day-month idx={idx}')


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


if __name__ == '__main__':
    unittest.main()
