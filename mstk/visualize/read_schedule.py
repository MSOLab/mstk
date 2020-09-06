import csv, json
from typing import List, Dict, Optional
from datetime import datetime
from dateutil.parser import parse as dt_parse

from mstk.schedule.ac_types import AcTypes
from mstk.schedule.interval import Interval
from mstk.schedule.schedule import Schedule


def read_machine_info(fname, schedule):
    with open(fname, "r", encoding="utf-8") as file_data:
        mc_info_dict = csv.DictReader(file_data)
        for contents in mc_info_dict:
            mc = schedule.add_machine(contents["mc_id"])
            for key, value in contents.items():
                mc.add_contents(key, value)


def read_job_info(fname, schedule):
    with open(fname, "r", encoding="utf-8") as file_data:
        job_info_dict = csv.DictReader(file_data)
        for contents in job_info_dict:
            job = schedule.add_job(contents["job_id"])
            for key, value in contents.items():
                job.add_contents(key, value)


def find_horizon(fname, horizon_start, horizon_end):

    if (horizon_start != None) and (horizon_end != None):
        return Interval(horizon_start, horizon_end)

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
        return Interval(horizon_start, horizon_end)


def read_schedule(proj_folder: str):

    ###
    ### Set params of the schedule
    ###

    with open(
        proj_folder + "\\metadata.json", "r", encoding="utf-8"
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
        ac_types = AcTypes("utf-8", True, True)
    else:
        ac_types = AcTypes(
            "utf-8", True, True, filename=proj_folder + "\\ac_types.json"
        )

    schedule = Schedule(input_dict["schedule_name"], horizon, ac_types)

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
            for key, value in contents.items():

                ac.add_contents(key, value)
    return schedule


def main():
    from mstk.test import sample_proj_folder

    sample_schedule = read_schedule(sample_proj_folder)
    print("Finished reading a sample schedule")


if __name__ == "__main__":
    main()
