from typing import Dict, Optional

import csv
import json
from datetime import datetime
from dateutil.parser import parse as dt_parse

from mstk.schedule.ac_types import AcTypesParam
from mstk.schedule.interval import Interval
from mstk.schedule.schedule import Schedule


def read_machine_info(fname: str, schedule: Schedule):
    """Reads machine information

    Args:
        fname (str): the file path
        schedule (Schedule): a schedule to add machines
    """
    with open(fname, "r", encoding="utf-8") as file_data:
        mc_info_dict = csv.DictReader(file_data)
        for contents in mc_info_dict:
            mc = schedule.add_machine(contents["mc_id"])
            for key, value in contents.items():
                mc.add_contents(key, value)


def read_job_info(fname: str, schedule: Schedule):
    """Reads job information

    Args:
        fname (str): the file path
        schedule (Schedule): a schedule to add jobs
    """

    with open(fname, "r", encoding="utf-8") as file_data:
        job_info_dict = csv.DictReader(file_data)
        for contents in job_info_dict:
            job = schedule.add_job(contents["job_id"])
            for key, value in contents.items():
                job.add_contents(key, value)


def find_horizon(
    fname: str,
    horizon_start: Optional[datetime],
    horizon_end: Optional[datetime],
):
    """Detects the earliest and the latest moment in the activity info
    if explicit start or end is not given

    Args:
        fname (str): the file path
        horizon_start (Optional[datetime]): the start of a horizon (if None, find the earliest moment of activities)
        horizon_end (Optional[datetime]): the end of a horizon (if None, find the latest moment of activities)

    Returns:
        Interval: a (compact) horizon of activities
    """

    if (horizon_start != None) and (horizon_end != None):
        interval: Interval = Interval(horizon_start, horizon_end)
        return interval

    else:
        min_horizon_start = datetime.max
        max_horizon_end = datetime.min

        with open(fname, "r", encoding="utf-8") as file_data:
            ac_info_dict = csv.DictReader(file_data)
            for contents in ac_info_dict:
                start = dt_parse(contents["start"])
                end = dt_parse(contents["end"])
                if (horizon_start == None) and (start < min_horizon_start):
                    min_horizon_start = start
                if (horizon_end == None) and (end > max_horizon_end):
                    max_horizon_end = end

        if horizon_start == None:
            horizon_start = min_horizon_start
        if horizon_end == None:
            horizon_end = max_horizon_end
        interval = Interval(horizon_start, horizon_end)
        return interval


def read_schedule(proj_folder: str):
    """[summary]

    Args:
        proj_folder (str): a project folder that contains metadata

    Raises:
        ValueError: [description]

    Returns:
        [type]: [description]
    """

    with open(
        proj_folder + "\\schedule_metadata.json", "r", encoding="utf-8"
    ) as file_data:
        input_dict = json.load(file_data)

    mc_info_fname = input_dict["file_info"]["machine_info"]
    job_info_fname = input_dict["file_info"]["job_info"]
    ac_info_full_name = (
        proj_folder + "\\" + input_dict["file_info"]["activity_info"]
    )
    horizon_start: Optional[datetime] = None
    if input_dict["horizon"]["start"] != None:
        horizon_start = dt_parse(input_dict["horizon"]["start"])

    horizon_end: Optional[datetime] = None
    if input_dict["horizon"]["end"] != None:
        horizon_end = dt_parse(input_dict["horizon"]["end"])

    horizon = find_horizon(ac_info_full_name, horizon_start, horizon_end)

    if input_dict["file_info"]["ac_types_info"] == None:
        ac_types = AcTypesParam()
    else:
        ac_types = AcTypesParam(filename=proj_folder + "\\ac_types.json")

    schedule: Schedule = Schedule(
        input_dict["schedule_name"], horizon, ac_types
    )

    ### Add machines
    if mc_info_fname != None:
        fname = proj_folder + "\\" + mc_info_fname
        read_machine_info(fname, schedule)
    else:
        mc_id_dict: Dict[str, bool] = {}

    ### Add jobs
    if job_info_fname != None:
        fname = proj_folder + "\\" + job_info_fname
        read_job_info(fname, schedule)
    else:
        job_id_dict: Dict[str, bool] = {}

    ### Add activities
    with open(ac_info_full_name, "r", encoding="utf-8") as file_data:
        ac_info_dict = csv.DictReader(file_data)
        for contents in ac_info_dict:
            mc_id = contents["mc_id"]
            ac_type = contents["ac_type"]
            job_id = contents["job_id"]
            start = dt_parse(contents["start"])
            end = dt_parse(contents["end"])

            if mc_info_fname == None:
                if mc_id not in mc_id_dict:
                    schedule.add_machine(mc_id)
                    mc_id_dict[mc_id] = True
            if job_info_fname == None:
                if job_id not in job_id_dict:
                    schedule.add_job(job_id)
                    job_id_dict[job_id] = True

            if ac_type == ac_types.operation:
                ac = schedule.add_operation(mc_id, job_id, start, end)
            elif ac_type == ac_types.breakdown:
                ac = schedule.add_breakdown(mc_id, start, end)
            else:
                raise ValueError(f"ac_type [{ac_type}] is not supported")
            for key, value in contents.items():
                if value != "":
                    ac.add_contents(key, value)
    return schedule


def main():
    from mstk.test import sample_proj_folder

    sample_schedule = read_schedule(sample_proj_folder)
    print("Finished reading a sample schedule")


if __name__ == "__main__":
    main()
