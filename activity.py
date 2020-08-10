""" Interval by datetime class definition
Created at 8th Aug. 2020
"""
from interval import Interval


class Activity:
    """activity with id, type, interval
    """

    ac_id: str
    ac_type: str
    interval: Interval
    op_id: str  # optional

    def __init__(self, ac_id: str, ac_type: str, interval: Interval):
        self.ac_id = ac_id
        self.ac_type = ac_type
        self.interval = interval

    def includes(self, moment) -> bool:
        """
        Args:
            moment: datetime or integer(as POSIX timestamp)

        Returns:
            bool: True if activity includes the moment
                  (including exactly start or end)
        """
        if self.interval.in_closed_interval(moment):
            return True
        return False

    def change_start_time(self, new_start_time):
        self.interval.start = new_start_time

    def change_end_time(self, new_end_time):
        self.interval.end = new_end_time
