"""
Stock param related functions
"""
from datetime import date, datetime, time
import dataclasses
from typing import List, Union
import numpy as np
import pandas as pd

from .enums import DfColumn


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
        self.symbol = symbol.upper()

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

    def set_from_date(self, from_date: Union[datetime, date]) -> date:
        """
        Set from date

        Args:
            from_date (Union[datetime, date]): from date (inclusive)
        """
        self._from_date = from_date

    def set_to_date(self, to_date: Union[datetime, date]) -> date:
        """
        Set to date

        Args:
            to_date (Union[datetime, date]): from date (inclusive)
        """
        self._to_date = to_date

    @staticmethod
    def _date(to_convert):
        return to_convert if isinstance(to_convert, date) else \
                to_convert.date()

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

    stock_param: StockParam
    """ Params of user request """
    data: Union[pd.DataFrame, List[str], object]
    """ Downloaded data """

    def __init__(
            self, stock_param: StockParam,
            data: Union[pd.DataFrame, List[str]]):
        self.stock_param = stock_param
        self.data = data

    @property
    def data_frame(self) -> pd.DataFrame:
        """
        Data as DataFrame

        Returns:
            pandas.DataFrame: data
        """
        return StockDownload.list_to_frame(self.data)\
            if isinstance(self.data, list) else self.data\
            if isinstance(self.data, pd.DataFrame) else pd.DataFrame(self.data)

    @staticmethod
    def download_of(data: object) -> object:
        """
        Factory

        Args:
            data (object): json data

        Returns:
            StockDownload: new object
        """
        stock_download = StockDownload(None, data)
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
            from_date (str): company name
            sector (str): industry or category
            currency (str, optional): currency

        Returns:
            Company: new object
        """
        return Company(code, symbol, name, sector, currency)


    def __str__(self) -> str:
        return f'{self.__class__.__name__}('\
               f'{self.symbol}, {self.name}, {self.code}, {self.sector}, '\
               f'{self.currency})'
