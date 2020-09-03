""" Interval by datetime class definition
Created at 8th Aug. 2020
"""
from mstk.schedule.interval import Interval
from typing import TYPE_CHECKING, Dict, Any

if TYPE_CHECKING:
    from mstk.schedule.machine import Machine
    from mstk.schedule.job import Job


class Activity:
    """activity with id, type, interval"""

    __ac_id: str
    ac_type: str
    interval: Interval
    contents: Dict[str, Any]
    # TODO: Consider adding a member -- mc: Machine

    def __init__(self, ac_id: str, ac_type: str, interval: Interval):
        self.__ac_id: str = ac_id
        self.ac_type: str = ac_type
        self.interval: Interval = interval
        self.contents: Dict[str, Any] = {}

    @property
    def ac_id(self):
        return self.__ac_id

    # @ac_id.setter
    # def ac_id(self, ac_id):
    #     self.__ac_id = ac_id

    def __repr__(self) -> str:
        return f"Activity {self.__ac_id}: {self.interval}"

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
        """
        Args:
            new_start_time ([type]): datetime.datetime instance or numeric
        """
        self.interval.change_start_time(new_start_time)

    def change_end_time(self, new_end_time):
        """
        Args:
            new_start_time ([type]): datetime.datetime instance or numeric
        """
        self.interval.change_end_time(new_end_time)

    def add_contents(self, key: str, value: Any):
        """adds additional contents to Machine

        Args:
            key (str): [description]
            value (Any): [description]
        """
        self.contents[key] = value


class Breakdown(Activity):
    def __init__(
        self,
        ac_id: str,
        ac_type: str,
        mc: "Machine",
        interval: Interval,
        # TODO: change ac_type as a global param
    ):
        self.__ac_id = ac_id
        self.ac_type = ac_type
        self.interval = interval
        self.mc = mc
        self.contents = {}

    @property
    def ac_id(self):
        return self.__ac_id

    def __repr__(self) -> str:
        return f"Breakdown {self.ac_id}: {self.interval}"


class Operation(Activity):
    def __init__(
        self,
        ac_id: str,
        ac_type: str,
        mc: "Machine",
        job: "Job",
        interval: Interval,
        # TODO: change ac_type as a global param
    ):
        self.__ac_id = ac_id
        self.ac_type = ac_type
        self.interval = interval
        self.mc = mc
        self.job = job
        self.contents = {}

    def __repr__(self) -> str:
        return f"Operation {self.__ac_id}: {self.interval}"

    @property
    def ac_id(self):
        return self.__ac_id


def main():
    ac_idle = Activity("test idle 1", "idle", Interval(2, 5))
    print("Original: ", ac_idle)

    ### change time test

    ac_idle.change_start_time(4)
    print("Changed start time: ", ac_idle)

    ac_idle.change_end_time(6)
    print("Changed end time: ", ac_idle)

    try:
        ac_idle.change_start_time(7)
    except ValueError as e:
        print("ValueError: ", e)

    try:
        ac_idle.change_end_time(1)
    except ValueError as e:
        print("ValueError: ", e)

    ### 'includes' test
    print("\n")
    print("is 3 included?:", ac_idle.includes(3))
    print("is 4 included?:", ac_idle.includes(4))
    print("is 5.5 included?:", ac_idle.includes(5.5))
    print("is 6 included?:", ac_idle.includes(6))
    print("is 7 included?:", ac_idle.includes(7))


if __name__ == "__main__":
    main()
