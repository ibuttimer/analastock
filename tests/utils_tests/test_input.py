"""
Unit tests for user input functions
"""
import unittest

from utils import get_input
from .mock_input import MockInputFunction


class TestInput(unittest.TestCase):
    """
    Unit tests for 'get_input' function
    """

    def test_no_val_no_param(self):
        """
        Test get_input with no validation function and no InputParam
        """
        with MockInputFunction(return_value='1'):

            user_ip = get_input("test input")
            self.assertEqual(user_ip, '1')

    def test_val_no_param(self):
        """
        Test get_input with no InputParam
        """
        with MockInputFunction(return_value='1'):

            def validate(value):
                return value

            user_ip = get_input("test input", validate=validate)
            self.assertEqual(user_ip, '1')


if __name__ == '__main__':
    unittest.main()
