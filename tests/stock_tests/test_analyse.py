"""
Unit tests for stock analyse functions
"""
from datetime import datetime, timedelta
import unittest
from stock import standardise_stock_param, StockParam
from stock.analyse import DATE_FORMAT, validate_period


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
        with self.subTest(msg='day from date'):
            ip_date = datetime(2022, 2, 1)
            period = validate_period(f'1d from {ip_date.strftime(DATE_FORMAT)}')
            self.assertIsNotNone(period)
            self.assertEqual(period.from_date, ip_date)
            self.assertEqual(period.to_date, ip_date + timedelta(days=1))

        with self.subTest(msg='day to date'):
            ip_date = datetime(2022, 2, 1)
            period = validate_period(f'1d to {ip_date.strftime(DATE_FORMAT)}')
            self.assertIsNotNone(period)
            self.assertEqual(period.from_date, ip_date - timedelta(days=1))
            self.assertEqual(period.to_date, ip_date)

if __name__ == '__main__':
    unittest.main()
