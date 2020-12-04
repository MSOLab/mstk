""" Schedule class definition
Created on 13th Aug. 2020
"""

__all__ = ["Schedule"]

from typing import TYPE_CHECKING, List, Dict, Iterator, Optional


import datetime as dt

from mstk.schedule.interval import Interval
from mstk.schedule.machine import Machine
from mstk.schedule.ac_types import AcTypesParam
from mstk.schedule.activity import Activity, Operation, Breakdown
from mstk.schedule.job import Job


class Schedule:
    """A set of machine schedules and tools to edit the machine schedules"""

    def __init__(
        self, schedule_id: str, horizon: Interval, ac_types_param: AcTypesParam
    ):
        self.__schedule_id: str = schedule_id
        self.__horizon: Interval = horizon

        self.__mc_id_list: List[str] = []
        self.__mc_dict: Dict[str, Machine] = {}

        self.__job_id_list: List[str] = []
        self.__job_dict: Dict[str, Job] = {}

        self.__ac_types_param: AcTypesParam = ac_types_param

    @property
    def schedule_id(self) -> str:
        return self.__schedule_id

    @property
    def horizon(self) -> Interval:
        return self.__horizon

    @property
    def mc_id_list(self) -> List[str]:
        return self.__mc_id_list

    @property
    def mc_dict(self) -> Dict[str, Machine]:
        return self.__mc_dict

    @property
    def job_id_list(self) -> List[str]:
        return self.__job_id_list

    @property
    def job_dict(self) -> Dict[str, Job]:
        return self.__job_dict

    @property
    def ac_types_param(self) -> AcTypesParam:
        return self.__ac_types_param

    def __repr__(self) -> str:
        return f"Schedule({self.schedule_id})"

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

    def add_machine(self, mc_id: str) -> Machine:
        """initializes a Machine object with mc_id

        Args:
            mc_id (str): an identifier of the machine

        Raises:
            KeyError: raised if the machine is already in this schedule

        Returns:
            Machine: the created Machine object
        """
        if mc_id in self.mc_id_list:
            raise KeyError(f"Machine {mc_id} already exists")
        else:
            mc = Machine(mc_id)
            self.mc_id_list.append(mc_id)
            self.mc_dict[mc_id] = mc
            mc.reset_schedule(self.horizon, self.ac_types_param)
        return mc

    def add_job(self, job_id: str) -> Job:
        """initializes a Job object with mc_id

        Args:
            job_id (str): an identifier of the job

        Raises:
            KeyError: raised if the job is already in this schedule

        Returns:
            Job: the created Job object
        """
        if job_id in self.job_id_list:
            raise KeyError(f"Job {job_id} already exists")
        else:
            job = Job(job_id)
            self.job_id_list.append(job_id)
            self.job_dict[job_id] = job
        return job

    def add_operation(
        self,
        mc_id: str,
        job_id: str,
        start: dt.datetime,
        end: dt.datetime,
        oper_id: str = "",
    ) -> Operation:
        """adds an operation to the corresponding mc_schedule and maps the activity to its job

        Args:
            mc_id (str): the id of the machine to assign
            job_id (str): the id of the job to assign
            start (datetime): start time of the activity
            end (datetime): end time of the activity
            oper_id (str, optional): the id operation (in default, a unique code in the mc_schedule is provided).

        Raises:
            KeyError: the machine id is not valid
            KeyError: the job id is not valid

        Returns:
            Operation: the created Operation object
        """
        if mc_id not in self.mc_id_list:
            raise KeyError(f"Machine {mc_id} does not exist")
        if job_id not in self.job_id_list:
            raise KeyError(f"Job {job_id} does not exist")
        ac_type = self.ac_types_param.operation
        mc = self.mc_dict[mc_id]
        job = self.job_dict[job_id]

        target_mc_schedule = mc.mc_schedule
        operation_count = target_mc_schedule.ac_cum_counts[ac_type] + 1
        if oper_id == "":
            operation_id = (
                f"{self.ac_types_param.operation}({mc_id}-{operation_count})"
            )
        else:
            operation_id = oper_id
        new_operation = Operation(
            operation_id, Interval(start, end), mc, job, self.ac_types_param
        )

        target_mc_schedule.add_activity(new_operation)
        job.add_operation(new_operation)

        return new_operation

    def add_breakdown(
        self, mc_id: str, start: dt.datetime, end: dt.datetime
    ) -> Breakdown:
        """adds an operation to the corresponding mc_schedule

        Args:
            mc_id (str): the id of the machine to assign
            start (datetime): start time of the activity
            end (datetime): end time of the activity

        Raises:
            KeyError: the machine id is not valid

        Returns:
            Breakdown: the created Breakdown object
        """
        if mc_id not in self.mc_id_list:
            raise KeyError(f"Machine {mc_id} does not exist")

        ac_type = self.ac_types_param.breakdown
        mc = self.mc_dict[mc_id]

        target_mc_schedule = mc.mc_schedule
        breakdown_count = target_mc_schedule.ac_cum_counts[ac_type] + 1
        breakdown_id = (
            f"{self.ac_types_param.breakdown}({mc_id}-{breakdown_count})"
        )

        new_activity = Breakdown(
            breakdown_id, Interval(start, end), mc, self.ac_types_param
        )
        target_mc_schedule.add_activity(new_activity)

        return new_activity

    # TODO: def add_setup_to_mc

    def transform_interval_to_horizon(
        self, interval: Interval, horizon: Interval, horz_overlap: str
    ) -> Optional[Interval]:
        """Transforms an interval to conform with a new horizon

        Args:
            interval (Interval): an interval to be processed
            horizon (Interval): a reference horizon
            horz_overlap (str): an option for intervals that overlaps to the horizon boundary

        Raises:
            ValueError: **horz_overlap** is not valid

        Returns:
            Optional[Interval]
                a trimmed interval, if exists
                None, otherwise
        """
        if horz_overlap in ["exclude"]:
            if (horizon.in_closed_interval(interval.start)) and (
                horizon.in_closed_interval(interval.end)
            ):
                return Interval(*interval.dt_range())
            else:
                return None
        elif horz_overlap in ["trim"]:
            new_interval = horizon.intersect(interval)
            return None if (new_interval == NotImplemented) else new_interval
        else:
            raise ValueError(f"horz_overlap {horz_overlap} is not valid ")
        return

    def transform(
        self,
        schedule_id: str,
        mc_id_list: List[str] = None,
        start: dt.datetime = None,
        end: dt.datetime = None,
        horz_overlap: str = "trim",
        **kwargs,
    ):
        """Transforms the schedule to conform with a new horizon

        Args:
            schedule_id (str): a name of the schedule
            mc_id_list (List[str], optional): a list of machine ids (if None, copied from **self.schedule**).
            start (dt.datetime, optional): a new value of the horizon  (if None, copied from **self.schedule**).
            end (dt.datetime, optional): a new value of the horizon. (if None, copied from **self.schedule**).
            horz_overlap (str, optional): an option for operations on the horizon boundary Defaults to "trim".

        Raises:
            ValueError: **start** or **end** does not conform to the horizon
            NotImplementedError: horz_overlap 'include' is prohibhited

        Returns:
            Schedule: a trimmed schedule
        """

        mc_id_list = self.mc_id_list if (mc_id_list == None) else mc_id_list

        start = self.horizon.start if (start == None) else start
        end = self.horizon.end if (end == None) else end
        new_horizon = Interval(start, end)
        if not (self.horizon.in_closed_interval(start)):
            raise ValueError(
                f"The new horizon {new_horizon} ends before the original start {start}"
            )
        if not (self.horizon.in_closed_interval(end)):
            raise ValueError(
                f"The new horizon {new_horizon} starts after the original end {end}"
            )

        # TODO: consider moving overlap_options to __init__.py
        overlap_options = ["include", "exclude", "trim"]
        if horz_overlap not in overlap_options:
            raise ValueError(
                f"horz_overlap {horz_overlap} is invalid -- try one of {overlap_options}"
            )
        elif horz_overlap in ["include"]:
            raise NotImplementedError(
                "horz_overlap option 'include' is prohibited to prevent an inconsistent mc_schedule"
            )

        new_schedule = Schedule(schedule_id, new_horizon, self.ac_types_param)

        for job_id in self.job_id_list:
            new_schedule.add_job(job_id)

        for mc_id in mc_id_list:
            new_mc = new_schedule.add_machine(mc_id)
            try:
                old_mc = self.mc_dict[mc_id]
            except:
                print(
                    f"Warning: Machine {mc_id} is not in schedule {self.schedule_id} (ignored)"
                )
                continue
            for ac in old_mc.ac_iter():
                if ac.ac_type == self.ac_types_param.idle:
                    continue

                new_interval = self.transform_interval_to_horizon(
                    ac.interval, new_horizon, horz_overlap
                )

                if new_interval != None:
                    if ac.ac_type == self.ac_types_param.operation:
                        job_id = ac.job.job_id
                        new_schedule.add_operation(
                            mc_id, job_id, *new_interval.dt_range()
                        )
                    elif ac.ac_type == self.ac_types_param.breakdown:
                        new_schedule.add_breakdown(
                            mc_id, *new_interval.dt_range()
                        )

        return new_schedule


def transform_test():
    ### Transformation test
    from mstk.test import sample_proj_folder
    from mstk.visualize.plot_schedule import PlotSchedule
    from mstk.read_schedule import read_schedule

    test_schedule = read_schedule(sample_proj_folder)
    mc_id_list = test_schedule.mc_id_list[
        : int(len(test_schedule.mc_id_list) / 2)
    ]
    new_schedule = test_schedule.transform(
        f"copy of {test_schedule.schedule_id}",
        start=dt.datetime(2020, 1, 1, 14),
        end=dt.datetime(2020, 1, 2, 9),
        horz_overlap="trim",
    )
    plot_schedule = PlotSchedule(new_schedule)
    plot_schedule.draw_Gantt()


def main():

    from mstk.test import sample_proj_folder
    from mstk.read_schedule import read_schedule

    test_schedule = read_schedule(sample_proj_folder)

    for mc in test_schedule.mc_iter():
        print(mc.mc_id)

        for operation in mc.operation_iter():
            print(operation)


if __name__ == "__main__":
    main()
    transform_test()
