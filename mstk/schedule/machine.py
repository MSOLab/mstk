""" MCSchedule class definition
Created at 10th Aug. 2020
"""
# common Python packages
import math
import datetime as dt
from typing import List, Dict, Tuple, Any, Iterator, Union

# defined packages
from mstk.schedule import to_dt
from mstk.schedule.interval import Interval
from mstk.schedule.activity import Activity, Operation, Breakdown
from mstk.schedule.ac_types import AcTypes


class Machine:
    mc_id: str
    contents: Dict[str, Any]

    def __init__(self, mc_id, ac_types):
        self.mc_id: str = mc_id
        self.ac_types = ac_types
        self.contents = {}
        # TODO fill the contents in

    @property
    def mc_schedule(self):
        try:
            return self.__mc_schedule
        except:
            raise

    def reset_schedule(self, horizon: Interval):
        self.__mc_schedule = MCSchedule(self.mc_id, horizon, self.ac_types)

    def ac_iter(self) -> Iterator[Activity]:
        """
        Yields:
            Iterator[Activity]
        """
        return self.__mc_schedule.ac_iter()

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

    def add_contents(self, key: str, value: Any):
        """adds additional contents to Machine

        Args:
            key (str): [description]
            value (Any): [description]
        """
        self.contents[key] = value


class MCSchedule:
    """A schedule of a machine in datetime format"""

    def __init__(self, mc_id: str, horizon: Interval, ac_types: AcTypes):
        self.__mc_id: str = mc_id
        self.horizon: Interval = horizon
        self.idle_type = ac_types.idle
        self.ac_id_list: List[str] = list()
        self.ac_dict: Dict[str, Activity] = dict()
        self.ac_types = ac_types
        # count of Activities by type: +1 when add_activity, -1 when delete_ac_id
        self.ac_counts = {ac_type: 0 for ac_type in ac_types.all_types}
        self.ac_cum_counts = {ac_type: 0 for ac_type in ac_types.all_types}

        self.initialize_idle()

    @property
    def mc_id(self):
        return self.__mc_id

    def initialize_idle(self):
        """Initialize MCSchedule's first idle Activity instance"""
        idle_id = self.make_ac_id_for_type(self.idle_type)
        initial_idle = Activity(idle_id, self.idle_type, self.horizon)
        self.ac_dict[initial_idle.ac_id] = initial_idle
        self.ac_id_list += [initial_idle.ac_id]
        self.ac_counts[self.idle_type] = 1
        self.ac_cum_counts[self.idle_type] = 1

    def make_ac_id_for_type(self, ac_type: str) -> str:
        """Make ac_id with postfix starting with number 1

        Args:
            ac_type (str): pre-defined ac_type to make new ID

        Returns:
            str: new ac_id
        """
        return_string = (
            f"{ac_type}({self.mc_id}-{self.ac_cum_counts[ac_type]})"
        )
        return return_string

    def ac_iter(self) -> Iterator[Activity]:
        """
        Yields:
            Iterator[Activity]
        """
        for ac_id in self.ac_id_list:
            yield self.ac_dict[ac_id]

    def operation_iter(self) -> Iterator[Operation]:
        """
        Yields:
            Iterator[Opearation]
        """
        for ac_id in self.ac_id_list:
            ac = self.ac_dict[ac_id]
            if ac.ac_type == self.ac_types.operation:
                yield ac

    def actual_ac_iter(self) -> Iterator[Union[Operation, Breakdown]]:
        """
        Yields:
            Iterator[Opearation, Breakdown]
        """
        for ac_id in self.ac_id_list:
            ac = self.ac_dict[ac_id]
            if ac.ac_type == self.ac_types.idle:
                continue
            else:
                yield ac

    def hbar_tuple_list(self) -> List[Tuple[dt.datetime, dt.timedelta]]:
        """horizontal bar tuple list for Gantt chart making

        Returns:
            List[Tuple[dt.datetime, dt.timedelta]]: Tuple of [start, duration]
        """
        return_list = list()
        for ac_id in self.ac_id_list:
            ac = self.ac_dict[ac_id]
            return_list.append(ac.interval.start_duration_tuple())
        return return_list

    def delete_ac_id(self, ac_id: str):
        """Delete Activity instance info by ac_id from ac_dict

        Args:
            ac_id (str)
        """
        _ac_type = self.ac_dict[ac_id].ac_type
        self.ac_counts[_ac_type] -= 1
        self.ac_id_list.remove(ac_id)
        self.ac_dict.pop(ac_id)

    def before_horizon_start(self, d_moment: dt.datetime) -> bool:
        """
        Args:
            d_moment (dt.datetime)

        Returns:
            bool: True if d_moment is before horizon start
        """
        return d_moment < self.horizon.start

    def after_horizon_end(self, d_moment: dt.datetime) -> bool:
        """
        Args:
            d_moment (dt.datetime)

        Returns:
            bool: True if d_moment is after horizon end
        """
        return d_moment > self.horizon.end

    def error_if_moment_outside_horizon(self, moment):
        """
        Args:
            moment ([type])

        Raises:
            ValueError: Given moment is before horizon start
            ValueError: Given moment is after horizon end
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

    def ac_id_of_moment(self, moment) -> str:
        """
        Args:
            moment ([type])

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

    def delete_ac_beyond_moment(self, moment):
        """delete all activities beyond moment
        the end of the activity occupying the moment is changed to the moment

        Args:
            moment ([type])
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
        if self.before_horizon_start(given_interval.start):
            return False
        if self.after_horizon_end(given_interval.end):
            return False
        return True

    def error_if_interval_outside_horizon(self, given_interval: Interval):
        if not self.in_horizon_interval(given_interval):
            err_str = f"Given interval {given_interval} not in horizon "
            err_str += f"{self.horizon} of MCSchedule of machine {self.mc_id}"
            raise ValueError(err_str)

    # TODO: use iterator
    # TODO: provide options for operations that overlays a boundary value
    def ac_id_list_of_interval(self, given_interval: Interval) -> List[str]:
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
        """
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
        return target_ac_type == self.idle_type

    def add_activity(self, ac: Activity) -> bool:
        """Try adding given Activity instance with given interval

        Args:
            ac (Activity): with ac_type and Interval set

        Returns:
            bool: True if addition of Activity was successful, False otherwise
        """
        _interval = ac.interval

        if (_interval.duration().total_seconds() == 0) and (
            _interval.end == self.horizon.end
        ):
            if ac.ac_type == self.idle_type:
                raise ValueError(
                    "An idle job with duration 0 is not allowed to insert"
                )
            self.ac_id_list += [ac.ac_id]
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
        target_ac_id = self.ac_id_list_of_interval(_interval)[0]
        target_ac = self.ac_dict[target_ac_id]
        target_ac_idx = self.ac_id_list.index(target_ac_id)

        added_ac_list: List[Activity] = list()

        new_end_time: dt.datetime
        if target_ac.interval.end != _interval.end:
            idle_id = self.make_ac_id_for_type(self.idle_type)
            new_end_time = target_ac.interval.end
            new_interval = Interval(_interval.end, new_end_time)
            idle_after_ac = Activity(idle_id, self.idle_type, new_interval)
            added_ac_list.append(idle_after_ac)
            self.ac_counts[self.idle_type] += 1
            self.ac_cum_counts[self.idle_type] += 1

        added_ac_list.append(ac)
        self.ac_counts[ac.ac_type] += 1
        self.ac_cum_counts[ac.ac_type] += 1

        new_start_time: dt.datetime
        if target_ac.interval.start != _interval.start:
            idle_id = self.make_ac_id_for_type(self.idle_type)
            new_start_time = target_ac.interval.start
            new_interval = Interval(new_start_time, _interval.start)
            idle_before_ac = Activity(idle_id, self.idle_type, new_interval)
            added_ac_list.append(idle_before_ac)
            self.ac_counts[self.idle_type] += 1
            self.ac_cum_counts[self.idle_type] += 1

        self.ac_counts[self.idle_type] -= 1
        self.delete_ac_id(target_ac_id)
        for added_ac in added_ac_list:
            self.ac_id_list.insert(target_ac_idx, added_ac.ac_id)
            self.ac_dict[added_ac.ac_id] = added_ac
        if ac.interval.duration() == 0:
            print(f"Warning: {ac} has duration of 0")
        return True

    def del_activities_in_interval(self, given_interval: Interval):
        """Delete all activities within given interval
        and fill empty space with idle activity

        Args:
            given_interval (Interval)
        """
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
            before_is_idle = ac_before_target.ac_type == self.idle_type
            if not before_is_idle:
                new_start_time = ac_before_target.interval.end

        after_is_idle: bool
        if last_ac_idx == len(self.ac_id_list) - 1:
            after_is_idle = False
            new_end_time = self.horizon.end
        else:
            ac_after_target = self.ac_dict[self.ac_id_list[last_ac_idx + 1]]
            after_is_idle = ac_after_target.ac_type == self.idle_type
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
            idle_id = self.make_ac_id_for_type(self.idle_type)
            new_idle_activity = Activity(
                idle_id, self.idle_type, Interval(new_start_time, new_end_time)
            )
            self.ac_id_list.insert(first_ac_idx, idle_id)
            self.ac_dict[idle_id] = new_idle_activity
            self.ac_counts[self.idle_type] += 1
            self.ac_cum_counts[self.idle_type] += 1

    def idle_interval_list(self, release_date) -> List[Interval]:
        """
        Args:
            release_date ([type])

        Returns:
            List[Interval]: list of idle intervals beyond release_date
        """
        return_list: List[Interval] = list()
        if self.after_horizon_end(release_date):
            return return_list
        for ac in self.ac_iter():
            if (
                ac.ac_type == self.idle_type
                and ac.interval.end >= release_date
            ):
                return_list.append(ac.interval)
        return return_list

    def last_ac_id_of_type(self, target_type: str) -> str:
        """Return ac_id of last Activity instance with target_type

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
        """Return interval of last Activity instance with target_type

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


def main():
    from mstk.schedule.activity import Operation, Breakdown
    from mstk.schedule.job import Job

    ac_types = AcTypes("utf-8", True, True)
    machine_1 = Machine("test machine 1", ac_types)
    machine_1.reset_schedule(Interval(0, 20))
    job_1 = Job("Job_1")
    mc_schedule_1 = machine_1.mc_schedule

    # add activity test
    ac_operation_1 = Operation(
        "test ops 1",
        ac_types.operation,
        machine_1,
        job_1,
        Interval(1, 3),
    )
    ac_setup_1 = Activity("test setup 1", ac_types.setup, Interval(0, 1))
    ac_breakdown_1 = Breakdown(
        "test brkdown 1", ac_types.breakdown, machine_1, Interval(4, 8)
    )
    mc_schedule_1.add_activity(ac_operation_1)
    mc_schedule_1.add_activity(ac_setup_1)
    mc_schedule_1.add_activity(ac_breakdown_1)

    print("iter begins")
    for ac in mc_schedule_1.actual_ac_iter():
        print(ac)
    print("iter ends")

    # for ac in mc_schedule_1.ac_iter():
    #     print(ac)

    # delete activity test
    print("\ntest ops 1 deleted")
    mc_schedule_1.del_activities_in_interval(ac_operation_1.interval)
    for ac in mc_schedule_1.ac_iter():
        print(ac)


if __name__ == "__main__":
    main()
