""" Interval by datetime class definition
Created on 8th Aug. 2020
"""
from typing import TYPE_CHECKING, Dict, Any, Tuple, Callable

import datetime as dt

from mstk.schedule.ac_types import AcTypesParam
from mstk.schedule.interval import Interval

if TYPE_CHECKING:
    from mstk.schedule.machine import Machine
    from mstk.schedule.job import Job

__all__ = ["Activity", "Idle", "Operation", "Breakdown"]


class Activity:
    """Unassigned activity with id, type, interval

    Warning:
        Do not use this class when assigning an activity to machines;

        Use Operation, Breakdown, Setup or their inherited classes
    """

    __slots__ = [
        "__ac_id",
        "__ac_types_param",
        "__ac_type",
        "__interval",
        "__contents",
    ]

    def __init__(
        self,
        ac_id: str,
        interval: Interval,
        ac_types_param: AcTypesParam,
    ):
        self.__ac_id: str = ac_id
        self.__ac_types_param = ac_types_param

        self.__ac_type: str = ac_types_param.activity
        self.__interval: Interval = interval
        self.__contents: Dict[str, Any] = {}

    @property
    def ac_id(self) -> str:
        return self.__ac_id

    @property
    def ac_type(self) -> str:
        return self.__ac_type

    @property
    def ac_types_param(self) -> AcTypesParam:
        return self.__ac_types_param

    @property
    def interval(self) -> Interval:
        return self.__interval

    @property
    def contents(self) -> Dict[str, Any]:
        return self.__contents

    def __repr__(self) -> str:
        return f"{self.ac_type}({self.__ac_id}): {self.interval}"

    def includes(self, moment: dt.datetime) -> bool:
        """Checks whether the activity contains {moment}

        Args:
            moment (dt.datetime): a moment to be checked

        Returns:
            bool: True if activity includes the moment
                  (including the exact start and the end)
        """

        if self.interval.in_closed_interval(moment):
            return True
        return False

    def change_start_time(self, new_start_time: dt.datetime):
        """Changes the start time of the current activity

        Args:
            new_start_time (dt.datetime): start time value to be changed into
        """

        self.interval.change_start_time(new_start_time)

    def change_end_time(self, new_end_time: dt.datetime):
        """Changes the end time of the current activity

        Args:
            new_end_time (datetime.datetime): end time to be changed into
        """

        self.interval.change_end_time(new_end_time)

    def add_contents(self, key: str, value: Any):
        """Adds supplementary information of the activity to a dictionary 'contents'

        Args:
            key (str): an id for the content
            value (Any): the value to be stored
        """

        self.contents[key] = value

    def dt_range(self) -> Tuple[dt.datetime, dt.datetime]:
        """Returns the start and end time of the activity in a tuple

        Returns:
            Tuple[dt.datetime, dt.datetime]: [description]
        """
        return self.interval.dt_range()

    def display_contents(self, func: Callable, **kwargs):
        """Prints all the contents (default)"""
        func(self.contents)


class Idle(Activity):
    """An idle activity assigned to a machine"""

    __slots__ = ["__ac_type", "__mc"]

    def __init__(
        self,
        ac_id: str,
        interval: Interval,
        mc: "Machine",
        ac_types_param: AcTypesParam,
    ):
        super().__init__(ac_id, interval, ac_types_param)
        self.__ac_type = ac_types_param.idle
        self.__mc = mc

    @property
    def ac_type(self):
        return self.__ac_type

    @property
    def mc(self):
        return self.__mc


class Breakdown(Activity):
    """A breakdown activity assigned to a machine"""

    __slots__ = ["__ac_type", "__mc"]

    def __init__(
        self,
        ac_id: str,
        interval: Interval,
        mc: "Machine",
        ac_types_param: AcTypesParam,
    ):
        super().__init__(ac_id, interval, ac_types_param)
        self.__ac_type = ac_types_param.breakdown
        self.__mc = mc

    @property
    def ac_type(self):
        return self.__ac_type

    @property
    def mc(self):
        return self.__mc


class Operation(Activity):
    """An operation activity assigned to a machine and a job"""

    __slots__ = ["__ac_type", "__mc", "__job"]

    def __init__(
        self,
        ac_id: str,
        interval: Interval,
        mc: "Machine",
        job: "Job",
        ac_types_param: AcTypesParam,
    ):

        super().__init__(ac_id, interval, ac_types_param)
        self.__ac_type = ac_types_param.operation
        self.__mc = mc
        self.__job = job

    @property
    def ac_type(self):
        return self.__ac_type

    @property
    def mc(self):
        return self.__mc

    @property
    def job(self):
        return self.__job


def main():
    ac_types_param = AcTypesParam()
    ac_unassigned = Activity("test ac 1", Interval(2, 5), ac_types_param)
    print("## Original: \n\t", ac_unassigned)

    ### change time test

    ac_unassigned.change_start_time(4)
    print("## Changed start time: \n\t", ac_unassigned)

    ac_unassigned.change_end_time(6)
    print("## Changed start time: \n\t", ac_unassigned)

    try:
        ac_unassigned.change_start_time(7)
    except ValueError as e:
        print("## (Intended) ## ValueError: ", e)

    try:
        ac_unassigned.change_end_time(1)
    except ValueError as e:
        print("## (Intended) ## ValueError: ", e)

    print("\n## <includes> test")
    print(f"is 3 included in {ac_unassigned}?:", ac_unassigned.includes(3))
    print(f"is 4 included in {ac_unassigned}?:", ac_unassigned.includes(4))
    print(f"is 5.5 included in {ac_unassigned}?:", ac_unassigned.includes(5.5))
    print(f"is 6 included in {ac_unassigned}?:", ac_unassigned.includes(6))
    print(f"is 7 included in {ac_unassigned}?:", ac_unassigned.includes(7))


if __name__ == "__main__":
    main()
