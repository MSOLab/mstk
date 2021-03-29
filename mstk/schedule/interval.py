""" Interval by datetime class definition
Created on 8th Aug. 2020
"""

from __future__ import annotations

__all__ = ["Interval"]

# common Python packages
import datetime as dt
from typing import Optional, Tuple

# defined packages
from mstk.schedule import to_dt


class Interval:
    """interval with start & end datetime value
    (start <= end) must hold true in initialization
    """

    __slots__ = ["__start", "__end"]
    __start: dt.datetime
    __end: dt.datetime

    def __init__(self, start: dt.datetime, end: dt.datetime):
        if start > end:
            raise ValueError("Interval start after end")
        self.__start = to_dt.to_dt_datetime(start)
        self.__end = to_dt.to_dt_datetime(end)

    @property
    def start(self):
        return self.__start

    @property
    def end(self):
        return self.__end

    def __repr__(self) -> str:
        return f"Interval({self.start}, {self.end})"

    def duration(self) -> dt.timedelta:
        """Returns duration of the interval in timedelta

        Returns:
            dt.timedelta: (end - start) timedelta value
        """

        return self.end - self.start

    def dt_range(self) -> Tuple[dt.datetime, dt.datetime]:
        """Returns a tuple of start and end time

        Returns:
            Tuple[datetime.datetime, datetime.datetime]: the start and end of the interval
        """

        return (self.start, self.end)

    def start_duration_tuple(self) -> Tuple[dt.datetime, dt.timedelta]:
        """Returns a tuple of start and duration

        Returns:
            Tuple[datetime.datetime, datetime.timedelta]: [start, duration]
        """
        return (self.start, self.end - self.start)

    def in_closed_interval(self, moment) -> bool:
        """Returns true if [moment] is in the interval

        Args:
            moment (datetime.datetime):

        Returns:
            bool:
        """
        _moment = to_dt.to_dt_datetime(moment)
        if self.start <= _moment and _moment <= self.end:
            return True
        else:
            return False

    def is_distinct(self, other) -> bool:
        """Returns true if two intervals are distinct (considering a point overlay)

        Args:
            other (Interval): an interval to be compared

        Raises:
            TypeError: {other} is not an interval instance

        Returns:
            bool: True if self and other are distinct
        """

        if isinstance(other, Interval):
            if self.end <= other.start or other.end <= self.start:
                return True
            else:
                return False
        else:
            raise TypeError(f"{other} is not an interval instance")

    def intersect(self, other) -> Optional[Interval]:

        """Returns the intersection of two intervals

        Args:
            other (Interval): an interval to be referred

        Raises:
            ValueError: {other} is not an interval instance

        Returns:
            Optional[Interval]: None if the intersection is empty
        """

        if isinstance(other, Interval):
            if not self.is_distinct(other):
                return Interval(
                    max([self.start, other.start]), min([self.end, other.end])
                )
            else:
                return None
        else:
            raise ValueError(f"{other} is not an interval instance")

    def change_start_time(self, new_start_time: dt.datetime):
        """Updates the start time after check validity

        Args:
            new_start_time (datetime.datetime): datetime.datetime instance or numeric

        Raises:
            ValueError: the interval range is invalid
        """
        dt_new_start_time = to_dt.to_dt_datetime(new_start_time)
        if dt_new_start_time > self.end:
            raise ValueError(
                f"The new start time {dt_new_start_time}"
                + f" comes after the end time {self.end}!"
            )
        else:
            self.__start = dt_new_start_time

    def change_end_time(self, new_end_time: dt.datetime):
        """Updates the end time after check validity

        Args:
            new_end_time (datetime.datetime): datetime.datetime instance or numeric

        Raises:
            ValueError: the interval range is invalid
        """
        dt_new_end_time = to_dt.to_dt_datetime(new_end_time)
        if self.start > dt_new_end_time:
            raise ValueError(
                f"The new end time {dt_new_end_time}"
                + f" precedes the start time {self.start}!"
            )
        else:
            self.__end = dt_new_end_time


def main():
    interval1 = Interval(2, 10)
    print("interval1:", interval1, "with duration", interval1.duration())
    interval2 = Interval(9, 11)
    print("interval2:", interval2, "with duration", interval2.duration())
    print("Is distinct?:", interval1.is_distinct(interval2))
    print(
        "Intersection of two interval1 & interval2:",
        interval1.intersect(interval2),
    )
    interval3 = Interval(11, 12)
    print(
        "Example interval3:", interval3, "with duration", interval3.duration()
    )
    print(
        "Intersection of interval1 & interval3:",
        interval1.intersect(interval3),
    )
    print([interval1, interval2, interval3])


if __name__ == "__main__":
    main()
