""" Interval by datetime class definition
Created at 8th Aug. 2020
"""
from mstk.schedule.ac_types import AcTypesParam
from mstk.schedule.interval import Interval
import datetime as dt
from typing import TYPE_CHECKING, Dict, Any, Tuple

if TYPE_CHECKING:
    from mstk.schedule.machine import Machine
    from mstk.schedule.job import Job


class Activity:
    """Unassigned activity with id, type, interval

    An user-defined activity type can be derived from this class
    """

    __slots__ = [
        "__ac_id",
        "__ac_types_param",
        "__ac_type",
        "__interval",
        "__contents",
    ]
    # TODO: Consider adding a member -- mc: Machine
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
    def ac_id(self):
        return self.__ac_id

    @property
    def ac_type(self):
        return self.__ac_type

    @property
    def ac_types_param(self):
        return self.__ac_types_param

    @property
    def interval(self):
        return self.__interval

    @property
    def contents(self):
        return self.__contents

    def __repr__(self) -> str:
        return f"{self.ac_type}({self.__ac_id}): {self.interval}"

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

    def change_start_time(self, new_start_time: dt.datetime):
        """[summary]

        Args:
            new_start_time (dt.datetime): start time to be changed into
        """

        self.interval.change_start_time(new_start_time)

    def change_end_time(self, new_end_time: dt.datetime):
        """
        Args:
            new_end_time (dt.datetime): start time to be changed into
        """
        self.interval.change_end_time(new_end_time)

    def add_contents(self, key: str, value: Any):
        """adds additional information of the machine to contents dictionary

        Args:
            key (str): [description]
            value (Any): [description]
        """
        self.contents[key] = value

    def dt_range(self) -> Tuple[dt.datetime, dt.datetime]:
        return self.interval.dt_range()


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

    ### 'includes' test
    print("\n")
    print("is 3 included?:", ac_unassigned.includes(3))
    print("is 4 included?:", ac_unassigned.includes(4))
    print("is 5.5 included?:", ac_unassigned.includes(5.5))
    print("is 6 included?:", ac_unassigned.includes(6))
    print("is 7 included?:", ac_unassigned.includes(7))


if __name__ == "__main__":
    main()
