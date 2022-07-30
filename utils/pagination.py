"""
Miscellaneous functions
"""
from typing import Any, Callable, List, Union


class Pagination():
    """ Class representing a pagination """

    items: List[Any]
    """ List of page items """
    page_num: int
    """ Current page number (one-based) """
    num_pages: int
    """ Total number of pages """
    page_size: int
    """ Number of items per page """
    transform_func: Callable[[List[Any]], List[Any]]
    """ Function to transform items to return """


    def __init__(
            self, items: List[Any], page_size: int = 10,
            transform_func: Callable[[object], List[Any]] = None) -> None:
        self.items = items
        self.transform_func = transform_func
        self.set_page_size(page_size)


    def set_page_size(self, page_size: int):
        """
        Set the page size

        Args:
            page_size (int): page size
        """
        self.page_size = page_size
        self.num_pages = int(len(self.items) / page_size)
        if self.num_pages * page_size < len(self.items):
            self.num_pages += 1
        self.page_num = 1


    def get_page(self, page_num: int) -> Union[List[Any], None]:
        """
        Get the items for the specified page

        Args:
            page_num (int): number of page to get (one-based)

        Returns:
            Union[List[Any], None]: items or None if invalid page num
        """
        page_items = None
        if 1 <= page_num <= self.num_pages:
            start = (page_num - 1) * self.page_size
            end = page_num * self.page_size
            page_items = self.items[start:end]
            self.page_num = page_num

            if self.transform_func:
                page_items = self.transform_func(page_items)

        return page_items


    def get_current_page(self) -> List[Any]:
        """
        Get the items for the current page

        Returns:
            List[Any]: items
        """
        return self.get_page(self.page_num)


    def next_page(self) -> Union[List[Any], None]:
        """
        Get the next page of items

        Returns:
            Union[List[Any], None]: items or None if unavailable
        """
        return self.get_page(self.page_num + 1)


    def previous_page(self) -> Union[List[Any], None]:
        """
        Get the previous page of items

        Returns:
            Union[List[Any], None]: items or None if unavailable
        """
        return self.get_page(self.page_num - 1)

    @property
    def is_last_page(self) -> bool:
        """
        Check if current page is last page

        Returns:
            bool: True if last page
        """
        return self.page_num == self.num_pages

    @property
    def is_first_page(self) -> bool:
        """
        Check if current page is first page

        Returns:
            bool: True if first page
        """
        return self.page_num == 1

    @property
    def has_next_page(self) -> bool:
        """
        Check if next page is available

        Returns:
            bool: True if available
        """
        return self.page_num < self.num_pages

    @property
    def has_previous_page(self) -> bool:
        """
        Check if previous page is available

        Returns:
            bool: True if available
        """
        return self.page_num > 1

    @property
    def num_items(self) -> bool:
        """
        Total number of items

        Returns:
            int: True if available
        """
        return len(self.items)
