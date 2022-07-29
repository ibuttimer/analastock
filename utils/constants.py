"""
App constants
"""

DEFAULT_CREDS_FILE = "creds.json"
""" Default name of Google credentials file """

DEFAULT_CREDS_PATH = "./"
"""
Default path to Google credentials file
Note: if a relative path is specified, it must be relative to the
      project root folder.
"""

DEFAULT_RAPID_CREDS_FILE = "rapid_creds.json"
""" Default name of RapidAPI credentials file """

DEFAULT_RAPID_CREDS_PATH = "./"
"""
Default path to RapidAPI credentials file
Note: if a relative path is specified, it must be relative to the
      project root folder.
"""

DEFAULT_DATA_PATH = "./data"
"""
Default path to data files
Note: if a relative path is specified, it must be relative to the
      project root folder.
"""

EXCHANGES_SHEET = 'exchanges'
""" Name of sheet for exchanges data """

COMPANIES_SHEET = 'companies'
""" Name of sheet for companies data """

# command keys
PAGE_UP = '+'
PAGE_DOWN = '-'
HELP = '?'
ABORT = '/'

MAX_LINE_LEN = 80
""" Max display line width """

FRIENDLY_DATE_FMT = '%d %b %Y'
