"""
Grid display functions
"""

from dataclasses import dataclass
from enum import Enum, unique
from typing import List, Tuple, Union
from utils import Colour, colorise


# markers for highlight layout when debugging
_DEBUG = False
GAP_CHAR = '*' if _DEBUG else ' '
EOL = '|' if _DEBUG else ''
# Note: EOL is treated as a ctrl character, so multi-cell lines don't align
# with the expected line width due to the extra EOL chars. If the excess line
# width equals the number of cells - 1, everything is ok.

FORMAT_WIDTH_MARK = '@width@'
@unique
class Marker(Enum):
    """ Class representing cell markers """
    UP = ('^', Colour.GREEN)
    NEUTRAL = ('-')
    DOWN = ('v', Colour.RED)
    TITLE = ('', Colour.GREY, Colour.YELLOW)

    def __init__(
            self, m_string: str, colour: Colour = None,
            on_colour: Colour = None):
        self._m_string = m_string
        self._colour = colour
        self._on_colour = on_colour

    @property
    def colour(self):
        """
        Marker colour

        Returns:
            Colour: colour
        """
        return self._colour

    @property
    def on_colour(self):
        """
        Marker on_colour

        Returns:
            Colour: on_colour
        """
        return self._on_colour

    @property
    def m_string(self):
        """
        Marker string

        Returns:
            str: string
        """
        return self._m_string


@dataclass
class Str():
    """ Class representing a colourised text string """

    text: str
    """ Display string, including any colour control chars """
    length: int
    """ Length of string, excluding any colour control chars """
    ctrl_len: int
    """ Length of control chars in display string """

    def __init__(self, text: str, length: int):
        self.text = text
        self.length = length
        self.ctrl_len = len(self.text) - self.length

    @staticmethod
    def unpack(text: Union[str, object] = None) -> Tuple:
        """
        Unpack a Str object or str

        Args:
            text (Union[str, Str], optional): object or if not specified self

        Returns:
            Tuple: tuple(
                bool: is Str object flag,
                str: display string
                length: display length
                ctrl_len: length of ctrl chars in string
            )
        """
        is_str = isinstance(text, Str)
        return is_str, \
                text.text if is_str else text, \
                text.length if is_str else len(text), \
                text.ctrl_len if is_str else 0


class FormatMixin:
    """ Mixin class supplying formatting functions """

    def format_str(self, text: Union[str, Str], fmt: str = None,
                    width: int = None) -> Str:
        """
        Format a string of text

        Args:
            text (Union[str, Str]): text to format
            fmt (str, optional): Format specification. Defaults to None.
            width (int, optional): width. Defaults to None.

        Returns:
            Str: formatted text
        """
        _, formatted, _, ctrl_len = Str.unpack(text)
        if fmt:
            req_width = fmt.find(FORMAT_WIDTH_MARK) >= 0
            # add incoming ctrl char len to required width
            fmt_str = fmt.replace(FORMAT_WIDTH_MARK, str(width + ctrl_len)) \
                            if width else fmt
            formatted = f'{formatted:{fmt_str}}'
        else:
            req_width = False

        # if there was a required len, reduce length by incoming ctrl char len
        return Str(f'{formatted}{EOL}',
                   len(formatted) - (ctrl_len if req_width else 0))

    def colorised_str(self, text: Union[str, Str], fmt: str = None,
                    width: int = None, marker: Marker = None) -> Str:
        """
        Format and colourise a string of text

        Args:
            text (Union[str, Str]): text to format
            fmt (str, optional): Format specification. Defaults to None.
            width (int, optional): width. Defaults to None.
            marker (Marker, optional): marker with colour information.
                                        Defaults to None.

        Returns:
            Str: formatted and colourised text tuple
        """
        formed_str = self.format_str(text, fmt=fmt, width=width)

        colours = {}
        if marker:
            colours['colour'] = marker.colour if marker.colour else None
            colours['on_colour'] = marker.on_colour\
                                    if marker.on_colour else None
        formed_str.text = colorise(formed_str.text, **colours)
        formed_str.ctrl_len = len(formed_str.text) - formed_str.length
        return formed_str

    def set_x_pos(self, x_pos: int) -> object:
        """
        Builder method to set the x position

        Args:
            x_pos (int): position

        Returns:
            FormatMixin: object inheriting FormatMixin
        """
        self.x_pos = x_pos
        return self

    def set_marker(self, marker: Marker) -> object:
        """
        Builder method to set the marker

        Args:
            marker (Marker): marker

        Returns:
            FormatMixin: object inheriting FormatMixin
        """
        self.marker = marker
        return self

    def set_fmt(self, fmt: str) -> object:
        """
        Builder method to set the format string

        Args:
            fmt (str): format string

        Returns:
            FormatMixin: object inheriting FormatMixin
        """
        self.fmt = fmt
        return self


class DCell(FormatMixin):
    """
    Class representing a display cell

    Args:
        FormatMixin (class): mixin supplying formatting functions
    """

    x_pos: int
    """ X position """
    marker: Marker
    """ Marker """
    fmt: str
    """ Format specification """

    def __init__(self, text: str, width: int, fmt: str = None):
        self.text = text
        self.width = width
        self.x_pos = None
        self.marker = None
        self.fmt = fmt
        # bind builder functions to class
        # DCell.set_x_pos = set_x_pos
        # DCell.set_marker = set_marker
        # DCell.set_fmt = set_fmt

    def formatted(self) -> Str:
        """
        Generate the formatted cell text

        Returns:
            Str: string to display tuple
        """
        return self.format_str(self.text, self.fmt, self.width)

    def colorised(self) -> Str:
        """
        Generate the formatted and colourised cell text

        Returns:
            Str: string to display tuple
        """
        return self.colorised_str(self.text, self.fmt, self.width, self.marker)

    @classmethod
    def blank_cell(cls, width: int = 1) -> object:
        """
        Generate a blank cell

        Args:
            width (int, optional): width. Defaults to 1.

        Returns:
            DCell: cell
        """
        return cls('', width=width, fmt=f'<{width}')


# TODO check FormatMixin variables

# def set_x_pos(self, x_pos: int) -> DCell:
#     """
#     Builder method to set the x position

#     Args:
#         x_pos (int): position

#     Returns:
#         DCell: cell object
#     """
#     self.x_pos = x_pos
#     return self

# def set_marker(self, marker: Marker) -> DCell:
#     """
#     Builder method to set the marker

#     Args:
#         marker (Marker): marker

#     Returns:
#         DCell: cell object
#     """
#     self.marker = marker
#     return self

# def set_fmt(self, fmt: str) -> DCell:
#     """
#     Builder method to set the format string

#     Args:
#         fmt (str): format string

#     Returns:
#         DCell: cell object
#     """
#     self.fmt = fmt
#     return self


class DRow(FormatMixin):
    """
    Class representing a display row

    Args:
        FormatMixin (class): mixin supplying formatting functions
    """

    cells: List[DCell]
    """ Cells in row """
    width: int
    """ Width of row """
    x_pos: int
    """ X position """
    marker: Marker
    """ Marker """
    fmt: str
    """ Format specification """

    def __init__(self, width: int = None):
        self.width = width
        self.cells = []
        self.x_pos = None
        self.marker = None
        self.fmt = None

    def add_cell(self, cell: Union[DCell, List[DCell]]):
        """
        Add a cell to the row

        Args:
            cell (Union[DCell, List[DCell]]): cell(s) to add
        """
        if isinstance(cell, DCell):
            cell = [cell]
        self.cells.extend(cell)


    def _formatted(
            self, left_margin: int, right_margin: int, gap: int,
            colourised: bool) -> str:
        """
        Generate the formatted row text

        Args:
            left_margin (int): left cell margin
            right_margin (int): right cell margin
            gap (int): inter-cell gap; combines with left and right
                       margin to created space between columns
            colourised (bool): generate colourised string flag

        Returns:
            str: string to display
        """
        line = ''
        l_str = ''.rjust(left_margin)
        r_str = ''.rjust(right_margin)
        g_str = ''.rjust(gap, GAP_CHAR)

        length = 0  # length excluding ctrl chars

        for idx, cell in enumerate(self.cells):
            add_gap = idx and idx < len(self.cells)

            formed_str = cell.colorised() if colourised else cell.formatted()
            cell_text = f'{g_str if add_gap else ""}{l_str}'\
                        f'{formed_str.text}{r_str}'

            length += len(cell_text) - formed_str.ctrl_len

            line = f'{line}{cell_text}'

        formed_line = Str(line, length)

        formed_row = self.colorised_str(
                        formed_line, self.fmt, self.width, self.marker)\
                if colourised else \
                        self.format_str(formed_line, self.fmt, self.width)

        return formed_row.text

    def formatted(
            self, left_margin: int = 0, right_margin: int = 0,
            gap: int = 0) -> str:
        """
        Generate the formatted row text

        Args:
            left_margin (int): left cell margin
            right_margin (int): right cell margin
            gap (int): inter-cell gap; combines with left and right
                       margin to created space between columns

        Returns:
            Str: string to display tuple
        """
        return self._formatted(left_margin, right_margin, gap, False)

    def colorised(
            self, left_margin: int = 0, right_margin: int = 0,
            gap: int = 0) -> str:
        """
        Generate the formatted and colourised row text

        Args:
            left_margin (int): left cell margin
            right_margin (int): right cell margin
            gap (int): inter-cell gap; combines with left and right
                       margin to created space between columns

        Returns:
            Str: string to display tuple
        """
        return self._formatted(left_margin, right_margin, gap, True)

    @classmethod
    def blank_row(cls, width: int = 1) -> object:
        """
        Generate a blank row

        Args:
            width (int, optional): width. Defaults to 1.

        Returns:
            DRow: row
        """
        row = cls(width=width)
        row.add_cell(
            DCell.blank_cell()
        )
        return row


class DGrid(FormatMixin):
    """
    Class representing a display grid

    Args:
        FormatMixin (class): mixin supplying formatting functions
    """

    rows: List[DRow]
    """ Rows in grid """
    width: int
    """ Width of grid """
    gap: int
    """ Inter-column gap """
    x_pos: int
    """ X position """
    marker: Marker
    """ Marker """
    fmt: str
    """ Format specification """

    def __init__(self, width: int, gap: int = 1):
        self.width = width
        self.gap = gap
        self.rows = []
        self.x_pos = None
        self.marker = None
        self.fmt = None

    def add_row(self, row: DRow):
        """
        Add a row to the grid

        Args:
            row (DRow): row to add
        """
        self.rows.append(row)

    def _generate(
            self, left_margin: int = 0, right_margin: int = 0,
            gap: int = 0, colourised: bool = True) -> str:
        """
        Generate the formatted row text

        Args:
            left_margin (int): left cell margin
            right_margin (int): right cell margin
            gap (int): inter-cell gap; combines with left and right
                       margin to created space between columns
            colourised (bool, optional): use colour flag. Defaults to True.

        Returns:
            str: string to display
        """
        line = ''
        params = {
            'left_margin': left_margin,
            'right_margin': right_margin,
            'gap': gap
        }

        for idx, row in enumerate(self.rows):
            generator = row.colorised if colourised else row.formatted
            # no backslash allow in f-string, use chr(0x0A) for '\n'
            line = f'{line}{chr(0x0A) if idx > 0 else ""}{generator(**params)}'

        return line

    def display(self, colourised: bool = True):
        """
        Display the grid

        Args:
            colourised (bool, optional): use colour flag. Defaults to True.
        """
        print(
            self._generate(gap=self.gap, colourised=colourised)
        )
