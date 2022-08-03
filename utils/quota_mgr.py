"""
Functions related to Google quota management
"""
from datetime import datetime
from enum import Enum, auto
from threading import RLock
from time import perf_counter_ns, sleep
from typing import Union
from .misc import get_env_setting
from .constants import (
    DEFAULT_READ_QUOTA, DEFAULT_WRITE_QUOTA,
    READ_QUOTA_ENV, WRITE_QUOTA_ENV
)


class TimeUnit(Enum):
    """ Enum representing time units """
    SECOND = auto()
    """ Second time unit """
    MINUTE = auto()
    """ Minute time unit """
    HOUR = auto()
    """ Hour time unit """


class LevelQuotaMgr():
    """
    Class representing a quota manger which ensures each operation takes
    the max allowed time, to prevent exceeding quota
    """

    _ns_per_op: int
    """ Nanoseconds per operation """
    _lock: RLock
    """ Lock """
    # https://docs.python.org/3/library/threading.html?highlight=rlock#threading.RLock
    _start: int
    """ Start point of current operation """


    def __init__(self, quota: int, unit: TimeUnit = TimeUnit.MINUTE) -> None:
        """
        Constructor

        Args:
            quota (int): quota
            unit (TimeUnit, optional):
                    time unit of quota. Defaults to TimeUnit.MINUTE.

        Raises:
            ValueError: if invalid quota
        """
        if unit in TimeUnit:
            # convert quota to nanoseconds per operation
            quota = int(quota)
            per_sec = int(quota if unit == TimeUnit.SECOND else \
                            quota / 60 if unit == TimeUnit.MINUTE else \
                            quota / 3600)
            self._ns_per_op = int(10**9 / per_sec)

            if self._ns_per_op <= 0:
                raise ValueError(f'Invalid quota: {quota} {unit}')
        else:
            raise ValueError(f'Invalid unit: {unit}')

        self.lock = RLock()

    def acquire(self):
        """
        Acquire the lock.
        Note: Must be called before operation begins
        """
        self.lock.acquire()
        self._start = perf_counter_ns()

    def release(self):
        """
        Release the lock.
        Note: Must be called after operation ends
        """
        duration = perf_counter_ns() - self._start
        if duration < self._ns_per_op:
            # throttle to not exceed rate
            sleep((self._ns_per_op - duration) / 10**9)

        self.lock.release()


class RateQuotaMgr():
    """
    Class representing a quota manger which limits the number of operations
    i a time period to a percentage of the max allowed, to prevent exceeding
    quota
    """

    _quota: int
    """ Quota """
    _unit: TimeUnit
    """ Quota time unit """
    _limit: int
    """ Limit at which to pause operations """
    _lock: RLock
    """ Lock """
    # https://docs.python.org/3/library/threading.html?highlight=rlock#threading.RLock
    _start: int
    """ Start point of current period """
    _end: int
    """ End point of current period """
    _count: int
    """ Number of operations performed in current period """


    def __init__(
                self, quota: int, unit: TimeUnit = TimeUnit.MINUTE,
                percent: int = 75) -> None:
        """
        Constructor

        Args:
            quota (int): quota
            unit (TimeUnit, optional):
                    time unit of quota. Defaults to TimeUnit.MINUTE.
            percent (int): percent of quota at which to pause operations.
                        Defaults to 90.

        Raises:
            ValueError: if invalid quota
        """
        if unit in TimeUnit:
            quota = int(quota)
            if quota <= 0:
                raise ValueError(f'Invalid quota: {quota} {unit}')

            self._quota = quota
            self._unit = unit
        else:
            raise ValueError(f'Invalid unit: {unit}')

        if percent < 1 or percent > 100:
            raise ValueError(f'Invalid percent: {percent}')
        self._limit = int(self._quota * percent / 100)

        self.lock = RLock()
        self._reset()

    def _reset(self):
        """ Reset the current period """
        self._start = datetime.now().timestamp()
        self._end = self._start + (1 if self._unit == TimeUnit.SECOND else \
                                60 if self._unit == TimeUnit.MINUTE else 3600)
        self._count = 0

    def acquire(self):
        """
        Acquire the lock.
        Note: Must be called before operation begins
        """
        self.lock.acquire()
        if datetime.now().timestamp() >= self._end:
            self._reset()
        self._count += 1

    def release(self):
        """
        Release the lock.
        Note: Must be called after operation ends
        """
        if self._count >= self._limit:
            # throttle to not exceed rate
            sleep(self._end - datetime.now().timestamp())

        self.lock.release()


MANAGERS = {}

def get_manager(name: str) -> Union[LevelQuotaMgr, RateQuotaMgr]:
    """
    Get quota manager

    Args:
        name (str): manager name

    Returns:
        Union[LevelQuotaMgr, RateQuotaMgr]: manager
    """
    if name not in MANAGERS:
        Manager = LevelQuotaMgr \
            if get_env_setting('QUOTA_MGR') == 'LevelQuotaMgr' else \
                RateQuotaMgr

        MANAGERS['read'] = Manager(
                        get_env_setting(WRITE_QUOTA_ENV, DEFAULT_WRITE_QUOTA)
                    )
        MANAGERS['write'] = Manager(
                        get_env_setting(READ_QUOTA_ENV, DEFAULT_READ_QUOTA)
                    )
    return MANAGERS[name]


def read_manager():
    """
    Get read quota manager

    Returns:
        Union[LevelQuotaMgr, RateQuotaMgr]: manager
    """
    return get_manager('read')


def write_manager():
    """
    Get write quota manager

    Returns:
        Union[LevelQuotaMgr, RateQuotaMgr]: manager
    """
    return get_manager('write')
