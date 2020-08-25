""" Schedule class definition
Created at 13th Aug. 2020
"""

from typing import List, Dict, Iterator
from interval import Interval
from mc_schedule import MCSchedule
from ac_types import AcTypes
from activity import Activity

# class StaticMCInfo:
#     """A storage of machine info that is not relevant to scheduling
#     """

#     # TODO: fill the contents in


class MCInfoEssential:
    """A storage of machine info that is used in scheduling
    """

    def __init__(self, machine_id: str):
        self.machine_id: str = machine_id

        # TODO: fill the contents in


class Schedule:
    """ A set of machine schedules and tools to edit the machine schedules
    """

    def __init__(self, schedule_id: str, horizon: Interval, ac_types: AcTypes):
        self.schedule_id: str = schedule_id
        self.horizon: Interval = horizon
        self.mc_id_list: List[str] = []
        self.mc_info_dict: Dict[str, MCInfoEssential] = {}
        self.mc_schedule_dict: Dict[str, MCSchedule] = {}
        self.ac_types: AcTypes = ac_types

    def __repr__(self) -> str:
        return f"Schedule ({self.schedule_id})"

    def mc_iter(self) -> Iterator[MCSchedule]:
        """
        Yields:
            Iterator[MCSchedule]:
        """
        for mc_schedule in self.mc_schedule_dict.values():
            yield mc_schedule

    def add_machine(self, machine_info: MCInfoEssential):
        machine_id = machine_info.machine_id
        if machine_id in self.mc_info_dict:
            raise KeyError(f"Machine {machine_id} already exists")
        else:
            self.mc_id_list += [machine_id]
            self.mc_info_dict[machine_id] = machine_info
            self.mc_schedule_dict[machine_id] = MCSchedule(
                machine_id, self.horizon, self.ac_types
            )

    def add_operation_to_mc(self, machine_id: str, job_info: str, start, end):
        if machine_id not in self.mc_info_dict:
            raise KeyError(f"Machine {machine_id} does not exist")
        ac_type = self.ac_types.operation
        machine_info = self.mc_info_dict[machine_id]
        # TODO: use mc info to create id
        # TODO: connect job info

        target_mc_schedule = self.mc_schedule_dict[machine_id]
        operation_count = target_mc_schedule.ac_cum_counts[ac_type] + 1
        operation_id = f"Operation({machine_id}-{operation_count})"
        new_activity = Activity(
            operation_id, self.ac_types.operation, Interval(start, end)
        )
        new_activity.job_info = job_info
        target_mc_schedule.add_activity(new_activity)

    def add_breakdown_to_mc(self, machine_id: str, start, end):
        if machine_id not in self.mc_info_dict:
            raise KeyError(f"Machine {machine_id} does not exist")
        ac_type = self.ac_types.breakdown
        machine_info = self.mc_info_dict[machine_id]
        # TODO: use mc info to create id

        target_mc_schedule = self.mc_schedule_dict[machine_id]
        breakdown_count = target_mc_schedule.ac_cum_counts[ac_type] + 1
        breakdown_id = f"Brkdwn({machine_id}-{breakdown_count})"
        new_activity = Activity(breakdown_id, ac_type, Interval(start, end))
        target_mc_schedule.add_activity(new_activity)

    # TODO: def add_setup_to_mc


def main():
    import csv
    import datetime as dt

    # from to_dt import to_dt_datetime
    # from datetime.datetime import strptime
    dt_format = "%m/%d/%Y %H:%M"
    ac_types = AcTypes("utf-8", True, True)
    horizon_start = dt.datetime.strptime("7/6/2020 00:00", dt_format)
    horizon_end = dt.datetime.strptime("7/11/2020 00:00", dt_format)
    horizon = Interval(horizon_start, horizon_end)
    test_schedule = Schedule("test schedule", horizon, ac_types)
    with open("test/test_schedule.csv", "r") as _inputfile:
        job_list = list(csv.reader(_inputfile))[1:]

    # create machine list
    machine_list = []
    for job in job_list:
        mc_id = job[1]
        if mc_id not in machine_list:
            machine_list += [mc_id]
            mc_info = MCInfoEssential(mc_id)
            test_schedule.add_machine(mc_info)

    # create job list
    for job in job_list:
        mc_id = job[1]
        start = dt.datetime.strptime(job[2], dt_format)
        end = dt.datetime.strptime(job[3], dt_format)
        job_info = job[4]
        test_schedule.add_operation_to_mc(mc_id, job_info, start, end)

    for mc_sched in test_schedule.mc_iter():
        print(mc_sched.mc_id)
        for ac in mc_sched.ac_iter():
            print(ac)


if __name__ == "__main__":
    main()

