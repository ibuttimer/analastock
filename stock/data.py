"""
Stock param related functions
"""
from datetime import date, datetime, time
import dataclasses
from typing import List, Union
import numpy as np
import pandas as pd

from .enums import DfColumn, CompanyColumn


@dataclasses.dataclass
class StockParam:
    """
    Class representing parameters for a stock
    """

    symbol: str
    """ Stock symbol """
    _from_date: Union[datetime, date]
    """ From date (inclusive) for data """
    _to_date: Union[datetime, date]
    """ To date (exclusive) for data """

    def __init__(self, symbol: str):
        self.symbol = symbol.strip().upper()
        self._from_date = datetime.now().date()
        self._to_date = self._from_date

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(' \
               f'{self.symbol}, {self._from_date}, {self._to_date})'

    @classmethod
    def stock_param_of(
            cls, symbol: str,
            from_date: Union[datetime, date],
            to_date: Union[datetime, date]
    ) -> object:
        """
        Factory method

        Args:
            symbol (str): stock symbol
            from_date (Union[datetime, date]): from date (inclusive)
            to_date (Union[datetime, date]): to date (exclusive)

        Returns:
            StockParam: new object
        """
        stock_param = cls(symbol)
        stock_param._from_date = from_date
        stock_param._to_date = to_date
        return stock_param

    def set_from_date(self, from_date: Union[datetime, date]):
        """
        Set from date

        Args:
            from_date (Union[datetime, date]): from date (inclusive)
        """
        self._from_date = from_date

    def set_to_date(self, to_date: Union[datetime, date]):
        """
        Set to date

        Args:
            to_date (Union[datetime, date]): from date (inclusive)
        """
        self._to_date = to_date

    def set_dates(self, params: object):
        """
        Set dates from specified StockParam

        Args:
            params (StockParam): object to set dates from
        """
        if isinstance(params, StockParam):
            self._from_date = params._from_date
            self._to_date = params._to_date

    @staticmethod
    def _date(to_convert):
        return to_convert.date() if isinstance(to_convert, datetime) else \
            to_convert

    @staticmethod
    def _datetime(to_convert):
        return to_convert if isinstance(to_convert, datetime) else \
            datetime.combine(to_convert, time.min)

    @property
    def from_date(self) -> date:
        """
        From date as date

        Returns:
            date: from date
        """
        return StockParam._date(self._from_date)

    @property
    def from_datetime(self) -> datetime:
        """
        From date as datetime

        Returns:
            date: from datetime
        """
        return StockParam._datetime(self._from_date)

    @property
    def to_date(self) -> date:
        """
        To date as date

        Returns:
            date: to date
        """
        return StockParam._date(self._to_date)

    @property
    def to_datetime(self) -> datetime:
        """
        To date as datetime

        Returns:
            date: to datetime
        """
        return StockParam._datetime(self._to_date)


@dataclasses.dataclass
class StockDownload:
    """
    Class representing a downloaded stock data
    """
    NO_RESPONSE = -1

    stock_param: StockParam
    """ Params of user request """
    data: Union[pd.DataFrame, List[str], dict]
    """ Downloaded data """
    status_code: int
    """ Response status code """

    def __init__(
            self, stock_param: Union[StockParam, None],
            data: Union[pd.DataFrame, List[str], dict],
            status_code: int = NO_RESPONSE):
        self.stock_param = stock_param
        self.data = data
        self.status_code = status_code

    @property
    def data_frame(self) -> pd.DataFrame:
        """
        Data as DataFrame

        Returns:
            pandas.DataFrame: data
        """
        return StockDownload.list_to_frame(self.data) \
            if isinstance(self.data, list) else self.data \
            if isinstance(self.data, pd.DataFrame) else pd.DataFrame(self.data)

    @property
    def response_ok(self):
        """
        Response was success flag

        Returns:
            bool: True if response was success, otherwise False
        """
        return self.status_code == 200

    @staticmethod
    def download_of(data: dict, status_code: int = NO_RESPONSE) -> object:
        """
        Factory

        Args:
            data (object): json data
            status_code (int): response status code

        Returns:
            StockDownload: new object
        """
        stock_download = StockDownload(None, data, status_code)
        return stock_download

    @staticmethod
    def list_to_frame(data: List[str]):
        """
        Convert data to a Pandas DataFrame

        Args:
            data (List[str]): data to convert

        Returns:
            Pandas.DataFrame: data DataFrame
        """
        # split comma-separated string into list of strings
        # https://numpy.org/doc/stable/reference/arrays.ndarray.html
        #
        # Setting arr.dtype is discouraged and may be deprecated in the future.
        # Setting will replace the dtype without modifying the memory
        # https://numpy.org/doc/stable/reference/generated/numpy.ndarray.dtype.html#numpy.ndarray.dtype
        data_records = np.array(
            [entry.split(",") for entry in data]
        )
        # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.from_records.html#pandas.DataFrame.from_records
        data_frame = pd.DataFrame.from_records(
            data_records, columns=DfColumn.titles())

        # set any nulls to 0
        data_frame = data_frame.where(data_frame != 'null', 0)

        # convert numeric columns
        # https://pandas.pydata.org/docs/reference/api/pandas.to_numeric.html
        for column in DfColumn.NUMERIC_COLUMNS:
            data_frame[column.title] = pd.to_numeric(data_frame[column.title])

        # convert date column
        # https://pandas.pydata.org/docs/reference/api/pandas.to_datetime.html#pandas.to_datetime
        data_frame[DfColumn.DATE.title] = pd.to_datetime(
            data_frame[DfColumn.DATE.title].str.lower(),
            infer_datetime_format=True
        )

        return data_frame


@dataclasses.dataclass
class Company:
    """
    Class representing a company
    """

    code: str
    """ Exchange code """
    symbol: str
    """ Stock symbol """
    name: str
    """ Company name """
    sector: str
    """ Industry or category """
    currency: str
    """ Stock currency """

    def __init__(
            self, code: str, symbol: str, name: str, sector: str,
            currency: str):
        self.code = code.upper()
        self.symbol = symbol.upper()
        self.name = name
        self.sector = sector
        self.currency = currency

    @classmethod
    def company_of(
            cls, code: str, symbol: str, name: str, sector: str,
            currency: str = None
    ) -> object:
        """
        Factory method

        Args:
            code (str): exchange code
            symbol (str): stock symbol
            name (str): company name
            sector (str): industry or category
            currency (str, optional): currency

        Returns:
            Company: new object
        """
        return Company(code, symbol, name, sector, currency)

    def get_column(self, col: CompanyColumn) -> str:
        """
        Get the value corresponding to the specified CompanyColumn

        Args:
            col (CompanyColumn): value to get

        Returns:
            str: value
        """
        return self.code if col == CompanyColumn.EXCHANGE else \
            self.symbol if col == CompanyColumn.SYMBOL else \
            self.name if col == CompanyColumn.NAME else \
            self.sector if col == CompanyColumn.SECTOR else \
            self.currency if col == CompanyColumn.CURRENCY else None

    def unpack(self) -> List[str]:
        """
        Unpack this object to a list suitable for saving to sheets

        Returns:
            List[str]: unpacked values
        """
        return [self.get_column(col) for col in CompanyColumn]

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(' \
               f'{self.symbol}, {self.name}, {self.code}, {self.sector}, ' \
               f'{self.currency})'
