"""
Mock input function
"""

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
