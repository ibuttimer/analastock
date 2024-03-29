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

DEFAULT_HELP_PATH = "./doc/help.txt"
"""
Default path to help files
Note: if a relative path is specified, it must be relative to the
      project root folder.
"""

META_DATA_FOLDER = "meta"
""" Folder under data path where meta-data samples are stored """

EXCHANGES_SHEET = 'exchanges'
""" Name of sheet for exchanges data """

COMPANIES_SHEET = 'companies'
""" Name of sheet for companies data """

EFT_SHEET = 'eft'
""" Name of sheet for Exchange Traded Fund data """

MUTUAL_SHEET = 'mutual'
""" Name of sheet for Mutual Fund data """

FUTURES_SHEET = 'futures'
""" Name of sheet for Futures data """

INDEX_SHEET = 'index'
""" Name of sheet for Index data """

# command keys
PAGE_UP = '+'
PAGE_DOWN = '-'
HELP = '?'
BACK_KEY = '/'
HOME_KEY = '!!'

MAX_LINE_LEN = 80
""" Max display line width """
MAX_SCREEN_HEIGHT = 24
""" Max screen height """

FRIENDLY_DATE_FMT = '%d %b %Y'

DEFAULT_GOOGLE_READ_QUOTA = 60
""" Google Sheets API: Read requests per minute per user """
DEFAULT_GOOGLE_WRITE_QUOTA = 60
""" Google Sheets API: Write requests per minute per user """
GOOGLE_READ_QUOTA_ENV = 'GOOGLE_READ_QUOTA'
""" Google Sheets API: Read requests/minute/user environment variable """
GOOGLE_WRITE_QUOTA_ENV = 'GOOGLE_WRITE_QUOTA'
""" Google Sheets API: Write requests/minute/user environment variable """
DEFAULT_RAPIDAPI_READ_QUOTA = 50
""" RapidAPI: Requests per minute """
RAPIDAPI_READ_QUOTA_ENV = 'RAPIDAPI_READ_QUOTA'
""" RapidAPI: Requests per minute environment variable """

DEFAULT_MAX_BACKOFF = 128
""" Max backoff time for truncated exponential backoff retry """
MAX_BACKOFF_ENV = 'MAX_BACKOFF'
"""
Max backoff time for truncated exponential backoff retry environment variable
"""

MAX_MULTI_ANALYSIS = 3
""" Max number of stocks to compare in multi analysis """
