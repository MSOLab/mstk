""" Interval by datetime class definition
Created at 8th Aug. 2020
"""
# common Python packages
import datetime as dt
from typing import Tuple

# defined packages
import to_dt


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
        """return (end - start) timedelta value
        """
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
