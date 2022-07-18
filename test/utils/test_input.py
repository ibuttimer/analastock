"""
Unit tests for user input functions
"""
import unittest
from utils import get_input


class MockInputFunction:
    """
    Class to mock builtin function 'input'

    See https://stackoverflow.com/a/56301794
    """
    def __init__(self, return_value=None):
        self.return_value = return_value
        self._orig_input_fn = __builtins__['input']

    def _mock_input_fn(self, prompt):
        print(prompt + str(self.return_value))
        return self.return_value

    def __enter__(self):
        __builtins__['input'] = self._mock_input_fn

    def __exit__(self, typ, value, traceback):
        __builtins__['input'] = self._orig_input_fn


class TestInput(unittest.TestCase):
    """
    Units tests for 'get_input' function
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
