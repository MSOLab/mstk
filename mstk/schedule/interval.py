""" Interval by datetime class definition
Created at 8th Aug. 2020
"""
# common Python packages
import datetime as dt
from typing import Tuple

# defined packages
from mstk.schedule import to_dt


class Interval:
    """interval with start & end datetime value
    (start <= end) must hold true in initialization
    """

    __slots__ = ["start", "end"]
    start: dt.datetime
    end: dt.datetime

    def __init__(self, start, end):
        if start > end:
            raise ValueError("Interval start after end!")
        self.start = to_dt.to_dt_datetime(start)
        self.end = to_dt.to_dt_datetime(end)

    def duration(self) -> dt.timedelta:
        """return (end - start) timedelta value"""
        return self.end - self.start

    def range_tuple(self) -> Tuple[dt.datetime, dt.datetime]:
        return (self.start, self.end)

    def __repr__(self) -> str:
        return f"Interval({self.start}, {self.end})"

    def start_duration_tuple(self) -> Tuple[dt.datetime, dt.timedelta]:
        return (self.start, self.end - self.start)

    def in_closed_interval(self, moment) -> bool:
        _moment = to_dt.to_dt_datetime(moment)
        if self.start <= _moment and _moment <= self.end:
            return True
        else:
            return False

    def is_distinct(self, other) -> bool:
        if isinstance(other, Interval):
            if self.end < other.start or other.end < self.start:
                return True
            else:
                return False
        else:
            print("Input is not an interval instance")
            raise NotImplementedError

    def intersect(self, other):
        if isinstance(other, Interval):
            if not self.is_distinct(other):
                return Interval(
                    max([self.start, other.start]), min([self.end, other.end])
                )
            else:
                print("No intersection exists")
                return NotImplemented
        else:
            print("Input is not an interval instance")
            return NotImplemented

    def change_start_time(self, new_start_time):
        """Update the start time after check validity

        Args:
            new_start_time ([type]): datetime.datetime instance or numeric

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
            self.start = dt_new_start_time

    def change_end_time(self, new_end_time):
        """Update the end time after check validity

        Args:
            new_end_time ([type]): datetime.datetime instance or numeric

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
            self.end = dt_new_end_time


def main():
    interval1 = Interval(2, 10)
    print(
        "Example interval1:", interval1, "with duration", interval1.duration()
    )
    interval2 = Interval(9, 11)
    print(
        "Example interval2:", interval2, "with duration", interval2.duration()
    )
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
