"""
PEP8 style unit tests
"""
import os
import unittest
import pycodestyle


class TestCodeFormat(unittest.TestCase):
    """ PEP8 test suite """

    @unittest.skipIf(
        os.environ.get('SKIP_PEP8', 'n').lower() == 'y',
        'PEP8 testing disabled'
    )
    def test_conformance(self):
        """Test conformance to PEP-8."""
        style = pycodestyle.StyleGuide(quiet=True, config_file='setup.cfg')
        result = style.check_files(['.'])

        self.assertEqual(
            result.total_errors, 0,
            f"Found code style errors (and warnings).{chr(0x0A)}"\
            f"{f'{chr(0x0A)}'.join(result.get_statistics())}"
        )
