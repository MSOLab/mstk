""" Schedule class definition
Created at 13th Aug. 2020
"""

from typing import List, Dict, Iterator
from mstk.schedule.interval import Interval
from mstk.schedule.machine import Machine
from mstk.schedule.ac_types import AcTypes
from mstk.schedule.activity import Activity, Operation
from mstk.schedule.job import Job
from datetime import datetime


class Schedule:
    """A set of machine schedules and tools to edit the machine schedules"""

    def __init__(self, schedule_id: str, horizon: Interval, ac_types: AcTypes):
        self.schedule_id: str = schedule_id
        self.horizon: Interval = horizon

        self.mc_id_list: List[str] = []
        self.mc_dict: Dict[str, Machine] = {}

        self.job_id_list: List[str] = []
        self.job_dict: Dict[str, Job] = {}

        self.ac_types: AcTypes = ac_types

    def __repr__(self) -> str:
        return f"Schedule ({self.schedule_id})"

    def mc_iter(self) -> Iterator[Machine]:
        """
        Yields:
            Iterator[Machine]:
        """
        for mc_id in self.mc_id_list:
            yield self.mc_dict[mc_id]

    def job_iter(self) -> Iterator[Job]:
        """
        Yields:
            Iterator[Job]:
        """
        for job_id in self.job_id_list:
            yield self.job_dict[job_id]

    def add_machine(self, mc_id: str):
        if mc_id in self.mc_id_list:
            raise KeyError(f"Machine {mc_id} already exists")
        else:
            mc = Machine(mc_id, self.ac_types)
            self.mc_id_list += [mc_id]
            self.mc_dict[mc_id] = mc
            mc.reset_schedule(self.horizon)

    def add_job(self, job_id: str):
        if job_id in self.job_id_list:
            raise KeyError(f"Job {job_id} already exists")
        else:
            job = Job(job_id)
            self.job_id_list += [job_id]
            self.job_dict[job_id] = job

    # def add_job(self, job:Job):

    def add_operation(
        self,
        mc_id: str,
        job_id: str,
        start: datetime,
        end: datetime,
        oper_id: str = "",
    ):
        if mc_id not in self.mc_id_list:
            raise KeyError(f"Machine {mc_id} does not exist")
        if job_id not in self.job_id_list:
            raise KeyError(f"Job {job_id} does not exist")
        ac_type = self.ac_types.operation
        mc = self.mc_dict[mc_id]
        job = self.job_dict[job_id]

        # TODO: use mc info to create id
        # TODO: connect job info

        target_mc_schedule = mc.mc_schedule
        operation_count = target_mc_schedule.ac_cum_counts[ac_type] + 1
        if oper_id == "":
            operation_id = f"Operation({mc_id}-{operation_count})"
        else:
            operation_id = oper_id
        new_operation = Operation(
            operation_id,
            self.ac_types.operation,
            mc,
            job,
            Interval(start, end),
        )
        # new_activity.job_info = job_info
        target_mc_schedule.add_activity(new_operation)
        job.add_operation(new_operation)

    def add_breakdown(self, mc_id: str, start: datetime, end: datetime):
        if mc_id not in self.mc_id_list:
            raise KeyError(f"Machine {mc_id} does not exist")

        ac_type = self.ac_types.breakdown
        mc = self.mc_dict[mc_id]
        # TODO: use mc info to create id

        target_mc_schedule = mc.mc_schedule
        breakdown_count = target_mc_schedule.ac_cum_counts[ac_type] + 1
        breakdown_id = f"Brkdwn({mc_id}-{breakdown_count})"
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

    from mstk.test import small_data_filename

    with open(small_data_filename, "r") as _inputfile:
        oper_list = list(csv.reader(_inputfile))[1:]

    # create machine and list
    machine_list = []
    job_list = []
    for operation in oper_list:
        mc_id = operation[1]
        if mc_id not in machine_list:
            machine_list += [mc_id]
            test_schedule.add_machine(mc_id)
        job_id = operation[4]
        if job_id not in job_list:
            job_list += [job_id]
            test_schedule.add_job(job_id)

    # create operation list
    for operation in oper_list:
        mc_id = operation[1]
        start = dt.datetime.strptime(operation[2], dt_format)
        end = dt.datetime.strptime(operation[3], dt_format)
        job_id = operation[4]

        test_schedule.add_operation(mc_id, job_id, start, end)

    for mc_sched in test_schedule.mc_iter():
        print(mc_sched.mc_id)
        for ac in mc_sched.ac_iter():
            print(ac)


if __name__ == "__main__":
    main()
