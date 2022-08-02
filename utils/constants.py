"""
App constants
"""

GOOGLE_CREDS_FILE_ENV = "GOOGLE_CREDS_FILE"
""" Google credentials file environment variable """
DEFAULT_GOOGLE_CREDS_FILE = "google_creds.json"
""" Default name of Google credentials file """

GOOGLE_CREDS_PATH_ENV = "GOOGLE_CREDS_PATH"
""" Path to Google credentials file environment variable """
DEFAULT_GOOGLE_CREDS_PATH = "./"
"""
Default path to Google credentials file
Note: if a relative path is specified, it must be relative to the
      project root folder.
"""

YAHOO_FINANCE_CREDS_FILE_ENV = 'YAHOO_FINANCE_CREDS_FILE'
""" RapidAPI YahooFinance Stocks credentials file environment variable """
DEFAULT_YAHOO_FINANCE_CREDS_FILE = "yahoo_finance_creds.json"
""" Default name of RapidAPI YahooFinance Stocks credentials file """

YAHOO_FINANCE_CREDS_PATH_ENV = 'YAHOO_FINANCE_CREDS_PATH'
"""
Path to RapidAPI YahooFinance Stocks credentials file environment variable
"""
DEFAULT_YAHOO_FINANCE_CREDS_PATH = "./"
"""
Default path to RapidAPI YahooFinance Stocks credentials file
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

EFT_SHEET = 'eft'
""" Name of sheet for Exchange Traded Fund data """

# command keys
PAGE_UP = '+'
PAGE_DOWN = '-'
HELP = '?'
ABORT = '/'

MAX_LINE_LEN = 80
""" Max display line width """

FRIENDLY_DATE_FMT = '%d %b %Y'
