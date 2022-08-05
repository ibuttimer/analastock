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
        # simple test, no boundaries
        for unit in ['d', 'w', 'm', 'y']:
            date_str = param.strftime(DATE_FORMAT)

            for time_dir in ['from', 'to']:

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
                        base_val + \
                            ((unit_count if time_dir == 'from' else \
                                -unit_count) * multiplier)
                }

                period_str = f'{unit_count}{unit} {time_dir} {date_str}'
                test_msg = f'{unit_count} {units[unit]} {time_dir} '\
                           f'date {date_str}'

                for cmt, padding in [('no padding', ''), ('padding', ' ')]:

                    with self.subTest(msg=f'{test_msg} {cmt}'):

                        period = validate_period(
                            # e.g. '1d from 10-02-2022'
                            f'{padding}{period_str}{padding}')
                        self.assertIsNotNone(period)
                        self.assertEqual(period.from_date,
                            param if time_dir == 'from' else \
                                param.replace(**update))
                        self.assertEqual(period.to_date,
                            param.replace(**update) if time_dir == 'from' else \
                                param)

                with self.subTest(msg=f'{period_str} trailing text'):

                    period = validate_period(f'{period_str} extra text')
                    self.assertIsNone(period)

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
                with self.subTest(
                        msg=f'{unit_count} day {time_dir} date {date_str}'):
                    period = validate_period(
                        f'{unit_count}d {time_dir} {date_str}')
                    self.assertIsNotNone(period)
                    self.assertEqual(period.from_date,
                        param if time_dir == 'from' else param - delta)
                    self.assertEqual(period.to_date,
                        param + delta if time_dir == 'from' else param)

        # month boundaries
        for param in [
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
        ]:
            #  1   2   3   4   5   6   7   8   9  10  11  12
            #[31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
            date_str = param.test_date.strftime(DATE_FORMAT)

            for time_dir in ['from', 'to']:
                with self.subTest(
                        msg=f'{param.step} month {time_dir} date {date_str}'):

                    period = validate_period(
                        f'{param.step}m {time_dir} {date_str}')
                    self.assertIsNotNone(period)

                    self.assertEqual(period.from_date,
                        param.test_date if time_dir == 'from' else \
                            param.to_ans)
                    self.assertEqual(period.to_date,
                        param.from_ans if time_dir == 'from' else \
                            param.test_date)

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
        period_str = f'ytd {test_date.strftime(DATE_FORMAT)}'
        for cmt, padding in [('no padding', ''), ('padding', ' ')]:

            with self.subTest(msg=f'{period_str} {cmt}'):
                period = validate_period(
                    f'{padding}{period_str}{padding}')
                self.assertEqual(
                    period.from_date, test_date.replace(month=1, day=1))
                self.assertEqual(period.to_date, test_date)

        with self.subTest(msg=f'{period_str} trailing text'):

            period = validate_period(f'{period_str} extra text')
            self.assertIsNone(period)


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
        for cmt, padding in [('no padding', ''), ('padding', ' ')]:
            with self.subTest(msg=f'{period_str} {cmt}'):

                period = validate_period(f'{padding}{period_str}{padding}')
                self.assertEqual(period.from_date, jan1)
                self.assertEqual(period.to_date, today)

        with self.subTest(msg=f'{period_str} trailing text'):

            period = validate_period(f'{period_str} extra text')
            self.assertIsNone(period)


    def test_period_dmy_dmy(self):
        """
        Test period validation for dmy to dmy
        """
        # dmy [to/from] dmy tests
        for param in [
                    (datetime(2022, 2, 1), datetime(2022, 3, 1), 'to'),
                    (datetime(2022, 3, 1), datetime(2022, 2, 1), 'from')
                ]:
            test_from, test_to, valid_dir = param
            for time_dir in ['from', 'to']:
                period_str = f'{test_from.strftime(DATE_FORMAT)} {time_dir} '\
                            f'{test_to.strftime(DATE_FORMAT)}'

                for cmt, padding in [('no padding', ''), ('padding', ' ')]:
                    with self.subTest(msg=f'{period_str} {cmt}'):

                        period = validate_period(
                            f'{padding}{period_str}{padding}')
                        if time_dir == valid_dir:
                            self.assertEqual(period.from_date, test_from)
                            self.assertEqual(period.to_date, test_to)
                        else:
                            self.assertIsNone(period)

                with self.subTest(msg=f'{period_str} trailing text'):

                    period = validate_period(f'{period_str} extra text')
                    self.assertIsNone(period)

if __name__ == '__main__':
    unittest.main()
