"""
Stock related enums
"""
from enum import Enum


class DfColumn(Enum):
    """ DataFrame columns """

    # np.datatime64 needs a unit
    # The date units are years (‘Y’), months (‘M’), weeks (‘W’), and days (‘D’),
    # while the time units are hours (‘h’), minutes (‘m’), seconds (‘s’), milliseconds (‘ms’)
    # https://numpy.org/doc/stable/reference/arrays.datetime.html

    DATE = ('Date', 'np.datetime64')
    OPEN = ('Open', 'np.float64')
    HIGH = ('High', 'np.float64')
    LOW = ('Low', 'np.float64')
    CLOSE = ('Close', 'np.float64')
    ADJ_CLOSE = ('AdjClose', 'np.float64')
    VOLUME = ('Volume', 'np.uint64')

    def __init__(self, title: str, d_type: str):
        self._title = title
        self._d_type = d_type

    @property
    def title(self):
        """
        Title of column

        Returns:
            str: title
        """
        return self._title

    @property
    def d_type(self):
        """
        Numpy dtype for column

        Returns:
            srt: dtype
        """
        return self._d_type

    @staticmethod
    def titles():
        """
        Get list of titles

        Returns:
            list: titles
        """
        return [col.title for col in DfColumn]

    @staticmethod
    def d_types():
        """
        Get column dtypes dict

        Returns:
            dict: dtypes dict
        """
        return {
            col.title: col.d_type for col in DfColumn
        }

    @staticmethod
    def d_types_list():
        """
        Get column dtypes list

        Returns:
            dict: dtypes list
        """
        return [
            (col.title, col.d_type) for col in DfColumn
        ]

# List of numeric columns
# init numeric columns after class declaration
DfColumn.NUMERIC_COLUMNS = [
    DfColumn.OPEN, DfColumn.HIGH, DfColumn.LOW, DfColumn.CLOSE,
    DfColumn.ADJ_CLOSE, DfColumn.VOLUME
]

class DfStat(Enum):
    """ DataFrame statistics """

    MIN = ('Min')
    MAX = ('Max')
    CHANGE = ('Change')
    PERCENT_CHANGE = ('PercentChange')

    def __init__(self, title: str):
        self._title = title

    @property
    def title(self):
        """
        Title of statistic

        Returns:
            str: title
        """
        return self._title

    def column_key(self, column: DfColumn):
        """
        Generate a key for the specified DataFrame column and this statistic

        Args:
            column (DfColumn): DataFrame column

        Returns:
            str: key
        """
        return f'{column.title}{self.title}'


class CompanyColumn(Enum):
    """
    Enum representing columns in companies worksheet
    """
    EXCHANGE = 1
    """ Exchange code """
    SYMBOL = 2
    """ Stock symbol """
    NAME = 3
    """ Company name """
    SECTOR = 4
    """ Industry or Category """
    