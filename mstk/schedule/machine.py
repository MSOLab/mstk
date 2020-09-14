""" Machine class definition
Created on 10th Aug. 2020
"""
from __future__ import annotations

__all__ = ["Machine", "MCSchedule"]

# common Python packages
from typing import List, Dict, Tuple, Any, Iterator, Union, Callable

import datetime as dt
import warnings

# defined packages
from mstk.schedule import to_dt
from mstk.schedule.interval import Interval
from mstk.schedule.activity import Activity, Idle, Operation, Breakdown
from mstk.schedule.ac_types import AcTypesParam


class Machine:
    __slots__ = ["__mc_id", "__contents", "__mc_schedule"]

    def __init__(
        self,
        mc_id: str,
    ):
        self.__mc_id: str = mc_id
        self.__contents: Dict[str, Any] = {}

    @property
    def mc_id(self):
        return self.__mc_id

    @property
    def contents(self):
        return self.__contents

    @property
    def mc_schedule(self):
        try:
            return self.__mc_schedule
        except:
            raise

    def reset_schedule(self, horizon: Interval, ac_types_param: AcTypesParam):
        """Reset the mc_schedule

        Args:
            horizon (Interval): a new horizon to be assigned
            ac_types_param (AcTypesParam): a container of ac types
        """
        self.__mc_schedule = MCSchedule(
            self.mc_id, self, horizon, ac_types_param
        )

    def ac_iter(self) -> Iterator[Activity]:
        """
        Yields:
            Iterator[Activity]
        """
        return self.__mc_schedule.ac_iter()

    def ac_iter_of_types(self, ac_type_list: List[str]) -> Iterator[Activity]:
        """
        Yields:
            Iterator[Activity]
        """
        return self.__mc_schedule.ac_iter_of_types(ac_type_list)

    def operation_iter(self) -> Iterator[Operation]:
        """
        Yields:
            Iterator[Operation]
        """
        return self.__mc_schedule.operation_iter()

    def actual_ac_iter(self) -> Iterator[Union[Operation, Breakdown]]:
        """
        Yields:
            Iterator[Union[Operation, Breakdown]]
        """
        return self.__mc_schedule.actual_ac_iter()

    def idle_ac_iter(self) -> Iterator[Idle]:
        """
        Yields:
            Iterator[Idle]
        """
        return self.__mc_schedule.idle_ac_iter()

    def add_contents(self, key: str, value: Any):
        """Adds supplementary information of the machine to a dictionary [contents]

        Args:
            key (str): an id for the content
            value (Any): the value to be stored
        """
        self.__contents[key] = value

    def display_contents(self, func: Callable, **kwargs):
        """Prints all the contents (default)"""
        func(self.contents)


class MCSchedule:
    """A schedule consists of activities on a machine"""

    def __init__(
        self,
        mc_id: str,
        mc: Machine,
        horizon: Interval,
        ac_types_param: AcTypesParam,
    ):
        self.__mc_id: str = mc_id
        self.__mc: Machine = mc
        self.__horizon: Interval = horizon
        self.__ac_id_list: List[str] = list()
        self.__ac_dict: Dict[str, Activity] = dict()
        self.__ac_types_param = ac_types_param

        # count of activities for each type:
        self.__ac_counts: Dict[str, int] = {
            ac_type: 0 for ac_type in ac_types_param.all_types
        }
        # cumulativly count activities to make a unique identifier
        self.__ac_cum_counts: Dict[str, int] = {
            ac_type: 0 for ac_type in ac_types_param.all_types
        }

        self.initialize_idle()

    @property
    def mc_id(self) -> str:
        return self.__mc_id

    @property
    def mc(self) -> Machine:
        return self.__mc

    @property
    def horizon(self) -> Interval:
        return self.__horizon

    @property
    def ac_id_list(self) -> List[str]:
        return self.__ac_id_list

    @property
    def ac_dict(self) -> Dict[str, Activity]:
        return self.__ac_dict

    @property
    def ac_types_param(self) -> AcTypesParam:
        return self.__ac_types_param

    @property
    def ac_counts(self) -> Dict[str, int]:
        return self.__ac_counts

    @property
    def ac_cum_counts(self) -> Dict[str, int]:
        return self.__ac_cum_counts

    def initialize_idle(self):
        """Initialize MCSchedule with an idle activity"""
        self.__ac_id_list = []
        self.__ac_dict = {}
        idle_type = self.ac_types_param.idle
        idle_id = self.make_ac_id_for_type(idle_type)
        initial_idle = Idle(
            ac_id=idle_id,
            interval=self.horizon,
            mc=self.mc,
            ac_types_param=self.ac_types_param,
        )

        self.ac_dict[idle_id] = initial_idle
        self.ac_id_list.append(idle_id)

        self.__ac_counts = {
            ac_type: 0 for ac_type in self.ac_types_param.all_types
        }
        self.__ac_cum_counts = {
            ac_type: 0 for ac_type in self.ac_types_param.all_types
        }
        self.ac_counts[self.ac_types_param.idle] = 1
        self.ac_cum_counts[self.ac_types_param.idle] = 1

    def make_ac_id_for_type(self, ac_type: str) -> str:
        """Makes ac_id with cumulative counts as the postfix

        Args:
            ac_type (str): pre-defined ac_type to make new ID

        Returns:
            str: new ac_id
        """
        return_string = f"{ac_type}-{self.mc_id}-{self.ac_cum_counts[ac_type]}"
        return return_string

    def ac_iter(self) -> Iterator[Activity]:
        """
        Yields:
            Iterator[Activity]
        """
        for ac_id in self.ac_id_list:
            yield self.ac_dict[ac_id]

    def ac_iter_of_types(self, ac_type_list: List[str]) -> Iterator[Activity]:
        """
        Yields:
            Iterator[Activity]
        """
        if not (
            all(
                (ac_type in self.ac_types_param.all_types)
                for ac_type in ac_type_list
            )
        ):
            raise KeyError(
                f"List {ac_type_list} contains an unsupported activity type"
            )
        for ac_id in self.ac_id_list:
            ac = self.ac_dict[ac_id]
            if ac.ac_type in ac_type_list:
                yield ac

    def operation_iter(self) -> Iterator[Operation]:
        """
        Yields:
            Iterator[Opearation]
        """
        for ac_id in self.ac_id_list:
            ac = self.ac_dict[ac_id]
            if ac.ac_type == self.ac_types_param.operation:
                yield ac

    def actual_ac_iter(self) -> Iterator[Union[Operation, Breakdown]]:
        """
        Yields:
            Iterator[Opearation, Breakdown, Activity]
        """
        for ac_id in self.ac_id_list:
            ac = self.ac_dict[ac_id]
            if ac.ac_type == self.ac_types_param.idle:
                continue
            else:
                yield ac

    def idle_ac_iter(self) -> Iterator[Idle]:
        """
        Yields:
            Iterator[Idle]
        """
        for ac_id in self.ac_id_list:
            ac = self.ac_dict[ac_id]
            if ac.ac_type != self.ac_types_param.idle:
                continue
            else:
                yield ac

    def hbar_tuple_list(self) -> List[Tuple[dt.datetime, dt.timedelta]]:
        """Returns a horizontal bar tuple list

        Warnings:
            Use an iterator ac_iter to retrieve activities

        Returns:
            List[Tuple[dt.datetime, dt.timedelta]]: Tuple of [start, duration]
        """
        warnings.warn("This module is replaced by ac_iter", DeprecationWarning)
        return_list = list()
        for ac_id in self.ac_id_list:
            ac = self.ac_dict[ac_id]
            return_list.append(ac.interval.start_duration_tuple())
        return return_list

    def delete_ac_id(self, ac_id: str):
        """Deletes Activity instance info by ac_id from ac_dict

        Args:
            ac_id (str)
        """
        _ac_type = self.ac_dict[ac_id].ac_type
        self.ac_counts[_ac_type] -= 1
        self.ac_id_list.remove(ac_id)
        self.ac_dict.pop(ac_id)

    def before_horizon_start(self, moment: dt.datetime) -> bool:
        """Check if d_moment starts before the horizon

        Args:
            moment (datetime.datetime)

        Returns:
            bool: True if d_moment is before horizon.start
        """
        return moment < self.horizon.start

    def after_horizon_end(self, moment: dt.datetime) -> bool:
        """Check if d_moment starts before the horizon

        Args:
            moment (datetime.datetime)

        Returns:
            bool: True if moment is after horizon.end
        """
        return moment > self.horizon.end

    def error_if_moment_outside_horizon(self, moment: dt.datetime) -> bool:
        """Check if moment is outside the horizon

        Args:
            moment (datetime.datetime)

        Raises:
            ValueError: Given moment is before horizon start
            ValueError: Given moment is after horizon end
        Returns:
            bool: True if no error is found
        """
        _moment = to_dt.to_dt_datetime(moment)
        if self.before_horizon_start(_moment):
            err_str = f"Moment {moment} before horizon start "
            err_str += f" {self.horizon.start} of machine {self.mc_id}"
            raise ValueError(err_str)
        if self.after_horizon_end(_moment):
            err_str = f"Moment {moment} after MCSchedule horizon"
            err_str += f" {self.horizon.end} of machine {self.mc_id}"
            raise ValueError(err_str)
        return True

    def ac_id_of_moment(self, moment: dt.datetime) -> str:
        """Returns the activity occupying moment

        Args:
            moment (datetime.datetime)

        Raises:
            SyntaxError: no Activity instance occupying moment

        Returns:
            str: ac_id of the Activity instance occupying moment
                 if moment is boundary, latter ac_id is returned
        """
        _moment = to_dt.to_dt_datetime(moment)
        self.error_if_moment_outside_horizon(_moment)
        return_id: str
        for ac in self.ac_iter():
            if ac.includes(_moment) and ac.interval.end != _moment:
                return_id = ac.ac_id
                break
        if "return_id" in locals():
            return return_id
        e_str = "No Activity instance occupying moment "
        e_str += f"{moment} of machine {self.mc_id}"
        raise SyntaxError(e_str)

    def delete_ac_beyond_moment(self, moment: dt.datetime):
        """Deletes all activities beyond moment
        the end of the activity occupying the moment is changed to the moment

        Args:
            moment (datetime.datetime)
        """
        _moment = to_dt.to_dt_datetime(moment)
        # If given moment is beyond MCSchedule horizon, end
        if _moment >= self.horizon.end:
            return

        _ac_id = self.ac_id_of_moment(_moment)
        last_ac = self.ac_dict[_ac_id]
        if last_ac.interval.start == _moment:
            last_maintained_idx = self.ac_id_list.index(_ac_id) - 1
        else:
            last_maintained_idx = self.ac_id_list.index(_ac_id)
            self.ac_dict[_ac_id].interval.end = _moment
        removal_ac_count = len(self.ac_id_list) - last_maintained_idx - 1

        for _ in range(removal_ac_count):
            _ac_type = self.ac_dict[self.ac_id_list[-1]].ac_type
            self.ac_counts[_ac_type] -= 1
            del self.ac_dict[self.ac_id_list[-1]]
            self.ac_id_list.pop()

    def in_horizon_interval(self, given_interval: Interval) -> bool:
        """Checks whether the given interval conforms to the horizon

        Args:
            given_interval (Interval): an interval to be checked

        Returns:
            bool: True if the given interval conforms to the horizon
        """
        if self.before_horizon_start(given_interval.start):
            return False
        if self.after_horizon_end(given_interval.end):
            return False
        return True

    def error_if_interval_outside_horizon(self, given_interval: Interval):
        """Checks if the given interval is outside the horizon

        Args:
            given_interval (Interval): an interval to be checked

        Raises:
            ValueError: the given interval does not conform to the horizon
        """
        if not self.in_horizon_interval(given_interval):
            err_str = f"Given interval {given_interval} not in horizon "
            err_str += f"{self.horizon} of MCSchedule of machine {self.mc_id}"
            raise ValueError(err_str)

    def ac_id_list_of_interval(self, given_interval: Interval) -> List[str]:
        """Returns a list of activities of the MCSchedule that conform to the given interval

        Args:
            given_interval (Interval): An interval to be examined

        Returns:
            List[str]: activity list
        """
        self.error_if_interval_outside_horizon(given_interval)
        return_list: List[str] = list()
        for ac in self.ac_iter():
            ac_end = ac.interval.end
            if given_interval.start < ac_end:
                return_list.append(ac.ac_id)
                if given_interval.end <= ac_end:
                    break
        return return_list

    def is_idle_only(self, given_interval: Interval) -> bool:
        """Check if the given interval contains a single activity

        Args:
            given_interval (Interval):

        Returns:
            bool: True if an idle Activity occupies given interval
        """
        ac_id_list = self.ac_id_list_of_interval(given_interval)
        # if multiple Activities occupy given interval, return False
        if len(ac_id_list) > 1:
            return False

        ac_id = ac_id_list[0]
        target_ac_type = self.ac_dict[ac_id].ac_type
        return target_ac_type == self.ac_types_param.idle

    def add_activity(self, ac: Activity) -> bool:
        """Tries to add given Activity instance with given interval

        Args:
            ac (Activity): with ac_type and Interval set

        Returns:
            bool: True if addition of Activity was successful, False otherwise
        """
        _interval = ac.interval

        if (_interval.duration().total_seconds() == 0) and (
            _interval.end == self.horizon.end
        ):
            if ac.ac_type == self.ac_types_param.idle:
                raise ValueError(
                    "An idle job with duration 0 is not allowed to insert"
                )
            self.ac_id_list.append(ac.ac_id)
            self.ac_dict[ac.ac_id] = ac
            self.ac_counts[ac.ac_type] += 1
            self.ac_cum_counts[ac.ac_type] += 1
            # target_ac = self.ac_dict[self.ac_id_list[-1]]
            print(f"Warning: {ac} has duration of 0")
            return True

        if not self.is_idle_only(_interval):
            _str = f"Impossible add_activity request on machine {self.mc_id} "
            _str += f"with given interval {_interval} and type {ac.ac_type}"
            raise ValueError(
                f"{_interval} is occupied in Machine {self.mc_id}"
            )
        # Only one activity (idle) is on the target interval
        target_ac_id = self.ac_id_list_of_interval(_interval)[0]
        target_ac = self.ac_dict[target_ac_id]
        target_ac_idx = self.ac_id_list.index(target_ac_id)

        idle_type = self.ac_types_param.idle

        added_ac_list: List[Activity] = list()
        new_end_time: dt.datetime

        if target_ac.interval.end != _interval.end:
            idle_id = self.make_ac_id_for_type(idle_type)
            new_end_time = target_ac.interval.end
            new_interval = Interval(_interval.end, new_end_time)
            idle_after_ac = Idle(
                idle_id, new_interval, self.mc, self.ac_types_param
            )
            added_ac_list.append(idle_after_ac)
            self.ac_counts[idle_type] += 1
            self.ac_cum_counts[idle_type] += 1

        added_ac_list.append(ac)
        self.ac_counts[ac.ac_type] += 1
        self.ac_cum_counts[ac.ac_type] += 1

        new_start_time: dt.datetime
        if target_ac.interval.start != _interval.start:
            idle_id = self.make_ac_id_for_type(idle_type)
            new_start_time = target_ac.interval.start
            new_interval = Interval(new_start_time, _interval.start)
            idle_before_ac = Idle(
                idle_id, new_interval, self.mc, self.ac_types_param
            )
            added_ac_list.append(idle_before_ac)
            self.ac_counts[idle_type] += 1
            self.ac_cum_counts[idle_type] += 1

        self.delete_ac_id(target_ac_id)

        for added_ac in added_ac_list:
            self.ac_id_list.insert(target_ac_idx, added_ac.ac_id)
            self.ac_dict[added_ac.ac_id] = added_ac

        if ac.interval.duration() == 0:
            print(f"Warning: {ac} has duration of 0")
        return True

    def del_activities_in_interval(self, given_interval: Interval):
        """Deletes all activities within given interval
        and fill empty space with idle activity

        Args:
            given_interval (Interval)
        """
        idle_type = self.ac_types_param.idle
        self.error_if_interval_outside_horizon(given_interval)

        target_ac_id_list = self.ac_id_list_of_interval(given_interval)
        first_ac_idx = self.ac_id_list.index(target_ac_id_list[0])
        last_ac_idx = self.ac_id_list.index(target_ac_id_list[-1])

        before_is_idle: bool
        if first_ac_idx == 0:
            before_is_idle = False
            new_start_time = self.horizon.start
        else:
            ac_before_target = self.ac_dict[self.ac_id_list[first_ac_idx - 1]]
            before_is_idle = ac_before_target.ac_type == idle_type
            if not before_is_idle:
                new_start_time = ac_before_target.interval.end

        after_is_idle: bool
        if last_ac_idx == len(self.ac_id_list) - 1:
            after_is_idle = False
            new_end_time = self.horizon.end
        else:
            ac_after_target = self.ac_dict[self.ac_id_list[last_ac_idx + 1]]
            after_is_idle = ac_after_target.ac_type == idle_type
            if after_is_idle:
                new_end_time = ac_after_target.interval.end
            else:
                new_end_time = ac_after_target.interval.start

        for ac_id in target_ac_id_list:
            self.delete_ac_id(ac_id)

        # if two neighboring operations if target_ops are idle,
        # ----------<=given interval=>----------------
        # -|=idle1=||====target_ops====||=idle2=|-----
        # remove the latter one and change the end time of former one
        # -|===============idle1================|-----
        if before_is_idle and after_is_idle:
            self.delete_ac_id(ac_after_target.ac_id)
            ac_before_target.change_end_time(new_end_time)

        # if only a neighboring operation of the first element
        # of target_ops are idle,
        # ----------<=given interval=>----------------
        # -|=idle=||====target_ops====||=job=|--------
        # change the end time of the idle operation
        # -|===========idle===========||=job=|--------
        if before_is_idle and not after_is_idle:
            ac_before_target.change_start_time(new_start_time)

        # if only a neighboring operation of the last element
        # of target_ops are idle,
        # ----------<=given interval=>----------------
        # -|=job=||====target_ops====||=idle=|--------
        # change the start time of the idle operation
        # -|=job=||===========idle===========|--------
        if not before_is_idle and after_is_idle:
            ac_after_target.change_start_time(new_start_time)

        # if either of neighboring operations of target_ops are not idle,
        # ----------<=given interval=>----------------
        # -|=job=||====target_ops======||=job=|-------
        # create idle job and put it in the target_idx_first sequence
        # -|=job=||========idle========||=job=|-------
        if not before_is_idle and not after_is_idle:
            idle_id = self.make_ac_id_for_type(idle_type)
            new_idle_activity = Idle(
                idle_id, idle_type, Interval(new_start_time, new_end_time)
            )
            self.ac_id_list.insert(first_ac_idx, idle_id)
            self.ac_dict[idle_id] = new_idle_activity
            self.ac_counts[idle_type] += 1
            self.ac_cum_counts[idle_type] += 1

    def idle_interval_list(self, release_date: dt.datetime) -> List[Interval]:
        """Returns a list of idle activities

        Args:
            release_date (datetime.datetime)

        Returns:
            List[Interval]: list of idle activities beyond release_date
        """
        return_list: List[Interval] = list()
        if self.after_horizon_end(release_date):
            return return_list
        for ac in self.ac_iter():
            if (
                ac.ac_type == self.ac_types_param.idle
                and ac.interval.end >= release_date
            ):
                return_list.append(ac.interval)
        return return_list

    def last_ac_id_of_type(self, target_type: str) -> str:
        """Returns ac_id of last Activity instance with target_type

        Args:
            target_type (str): an ac_type value

        Returns:
            str: ac_id, "" if no such Activity instance
        """
        target_ac_id: str = ""
        for ac_id in reversed(self.ac_id_list):
            if self.ac_dict[ac_id].ac_type == target_type:
                target_ac_id = ac_id
                break
        return target_ac_id

    def last_ac_interval_of_type(self, target_type: str) -> Interval:
        """Returns interval of last Activity instance with target_type

        Args:
            target_type (str): an ac_type value

        Returns:
            Interval: interval of the Activity instance,
                      (start, start) if no Activity of target_type
        """
        return_interval = Interval(self.horizon.start, self.horizon.start)
        for ac_id in reversed(self.ac_id_list):
            ac = self.ac_dict[ac_id]
            if ac.ac_type == target_type:
                return_interval = ac.interval
                break
        return return_interval

    def intersection(self, other: "MCSchedule"):
        # self.actual_ac_iter()
        raise NotImplementedError()


def main():
    from mstk.schedule.job import Job

    ac_types_param = AcTypesParam()
    machine_1 = Machine("test machine 1")
    machine_1.reset_schedule(Interval(0, 20), ac_types_param)
    job_1 = Job("Job_1")
    mc_schedule_1 = machine_1.mc_schedule

    # add activity test
    ac_operation_1 = Operation(
        "test ops 1", Interval(1, 3), machine_1, job_1, ac_types_param
    )
    ac_breakdown_1 = Breakdown(
        "test brkdown 1",
        Interval(4, 8),
        machine_1,
        ac_types_param,
    )
    mc_schedule_1.add_activity(ac_operation_1)
    mc_schedule_1.add_activity(ac_breakdown_1)

    print("ac_iter begins")
    for ac in mc_schedule_1.ac_iter():
        print(ac)
    print("ac_iter ends")

    print("\nactual_iter begins")
    for ac in mc_schedule_1.actual_ac_iter():
        print(ac)
    print("actual_iter ends")

    # delete activity test
    print("\ntest ops 1 deleted")
    mc_schedule_1.del_activities_in_interval(ac_operation_1.interval)
    for ac in mc_schedule_1.ac_iter():
        print(ac)

    print("\nidle_iter")
    for ac in mc_schedule_1.ac_iter_of_types(["Idle"]):
        print(ac)

    # print(mc_schedule_1.ac_id_list_of_interval(Interval(5, 6)))

    # print(mc_schedule_1.intersection(mc_schedule_1))


if __name__ == "__main__":
    main()
