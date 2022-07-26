"""
Unit tests for stock analyse functions
"""
from datetime import datetime, timedelta, time
import unittest
from collections import namedtuple
from stock import standardise_stock_param, StockParam
from stock.analyse import DATE_FORMAT, validate_period


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
        self.assertEqual(stock_param.from_date, first_feb)


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
        self.assertEqual(stock_param.to_date, first_mar)


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
        self.assertEqual(stock_param.to_date, first_jan)


    def test_period(self):
        """
        Test period validation
        """
        units = {
            'd': 'day',
            'm': 'month',
            'y': 'year'
        }

        # NB: don't use future test dates

        unit_count = 2
        param = datetime(2022, 6, 10)
        # simple test, no boundaries
        for unit in ['d', 'm', 'y']:
            date_str = param.strftime(DATE_FORMAT)

            for time_dir in ['from', 'to']:
                with self.subTest(msg=f'{unit_count} {units[unit]} {time_dir} date {date_str}'):

                    base_val = param.year if unit == 'y' else \
                                param.month if unit == 'm' else param.day
                    update = {
                        f'{units[unit]}': base_val +
                                            (unit_count if time_dir == 'from' else -unit_count)
                    }

                    period = validate_period(
                        # e.g. '1d from 10-02-2022'
                        f'{unit_count}{unit} {time_dir} {date_str}')
                    self.assertIsNotNone(period)
                    self.assertEqual(period.from_date,
                        param if time_dir == 'from' else param.replace(**update))
                    self.assertEqual(period.to_date,
                        param.replace(**update) if time_dir == 'from' else param)

        # day boundaries
        unit_count = 1
        for param in [
            datetime(2022, 1, 1), datetime(2021, 12, 31),   # end of year
            datetime(2020, 2, 28), datetime(2022, 2, 28),   # leap/non-leap year
            datetime(2021, 9, 30), datetime(2021, 8, 31)
        ]:
            date_str = param.strftime(DATE_FORMAT)

            delta = timedelta(days=unit_count)
            for time_dir in ['from', 'to']:
                with self.subTest(msg=f'{unit_count} day {time_dir} date {date_str}'):
                    period = validate_period(
                        f'{unit_count}d {time_dir} {date_str}')
                    self.assertIsNotNone(period)
                    self.assertEqual(period.from_date,
                        param if time_dir == 'from' else param - delta)
                    self.assertEqual(period.to_date,
                        param + delta if time_dir == 'from' else param)

        # month boundaries
        for param in [
            #       test_date           date for from period  date for to period
            # end of year
            Param(datetime(2022, 1, 1), datetime(2022, 2, 1), datetime(2021, 12, 1), 1),
            Param(datetime(2021, 12, 31), datetime(2022, 1, 31), datetime(2021, 11, 30), 1),
            # leap year
            Param(datetime(2020, 2, 28), datetime(2020, 3, 28), datetime(2020, 1, 28), 1),
            # non-leap year
            Param(datetime(2022, 2, 28), datetime(2022, 3, 31), datetime(2022, 1, 31), 1),
            # end of month
            Param(datetime(2021, 9, 29), datetime(2021, 10, 29), datetime(2021, 8, 29), 1),
            Param(datetime(2021, 9, 30), datetime(2021, 10, 31), datetime(2021, 8, 31), 1),
            Param(datetime(2021, 9, 30), datetime(2021, 11, 30), datetime(2021, 7, 31), 2),
            # need 2 months gap to test 31th; mar-may-jul or aug-sep-dec
            Param(datetime(2021, 5, 31), datetime(2021, 7, 31), datetime(2021, 3, 31), 2)
        ]:
            #  1   2   3   4   5   6   7   8   9  10  11  12
            #[31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
            date_str = param.test_date.strftime(DATE_FORMAT)

            for time_dir in ['from', 'to']:
                with self.subTest(msg=f'{param.step} month {time_dir} date {date_str}'):

                    period = validate_period(
                        f'{param.step}m {time_dir} {date_str}')
                    self.assertIsNotNone(period)

                    self.assertEqual(period.from_date,
                        param.test_date if time_dir == 'from' else param.to_ans)
                    self.assertEqual(period.to_date,
                        param.from_ans if time_dir == 'from' else param.test_date)

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


if __name__ == '__main__':
    unittest.main()
