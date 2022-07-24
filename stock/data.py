"""
Stock param related functions
"""
from datetime import datetime
import dataclasses
from typing import List, Union
import numpy as np
import pandas as pd

from .enums import DfColumn


@dataclasses.dataclass
class StockParam:
    """
    Class representing a stock
    """

    symbol: str
    """ Stock symbol """
    from_date: datetime
    """ From date (inclusive) for data """
    to_date: datetime
    """ To date (exclusive) for data """

    def __init__(self, symbol: str):
        self.symbol = symbol.upper()

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(' \
               f'{self.symbol}, {self.from_date}, {self.to_date})'

    @staticmethod
    def stock_param_of(
        symbol: str, from_date: datetime, to_date: datetime) -> object:
        """
        Factory

        Args:
            symbol (str): stock symbol
            from_date (datetime): from date (inclusive)
            to_date (datetime): to date (exclusive)

        Returns:
            StockParam: new object
        """
        stock_param = StockParam(symbol)
        stock_param.from_date = from_date
        stock_param.to_date = to_date
        return stock_param


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
        data_frame = pd.DataFrame.from_records(data_records, columns=DfColumn.titles())

        # convert numeric columns
        # https://pandas.pydata.org/docs/reference/api/pandas.to_numeric.html
        for column in DfColumn.NUMERIC_COLUMNS:
            data_frame[column.title] = pd.to_numeric(data_frame[column.title])

        # convert date column
        # https://pandas.pydata.org/docs/reference/api/pandas.to_datetime.html#pandas.to_datetime
        data_frame[DfColumn.DATE.title] = pd.to_datetime(
            data_frame[DfColumn.DATE.title].str.lower(), infer_datetime_format=True
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

    def __init__(self, code: str, symbol: str, name: str, sector: str):
        self.code = code.upper()
        self.symbol = symbol.upper()
        self.name = name
        self.sector = sector

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(' \
               f'{self.symbol}, {self.name}, {self.code}, {self.sector})'
