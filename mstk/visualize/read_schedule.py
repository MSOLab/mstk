import csv, json
from dateutil.parser import parse as dt_parse

from mstk.schedule.ac_types import AcTypes
from mstk.schedule.interval import Interval
from mstk.schedule.schedule import Schedule


def read_schedule(proj_folder: str):

    ###
    ### Set params of the schedule
    ###

    with open(
        proj_folder + "\\metadata.json", "r", encoding="utf-8"
    ) as file_data:
        input_dict = json.load(file_data)

    # TODO: implement auto setting for the horizon
    horizon_start = dt_parse(input_dict["horizon"]["start"])
    horizon_end = dt_parse(input_dict["horizon"]["end"])
    horizon = Interval(horizon_start, horizon_end)
    ac_types = AcTypes(
        "utf-8", True, True, filename=proj_folder + "\\ac_types.json"
    )

    # TODO: implement ac_types as a global param

    schedule = Schedule(input_dict["schedule_name"], horizon, ac_types)

    ###
    ### Add machines
    ###
    mc_info_fname = input_dict["file_info"]["machine_info"]
    with open(
        proj_folder + "\\" + mc_info_fname, "r", encoding="utf-8"
    ) as file_data:
        mc_info_dict = csv.DictReader(file_data)
        for item in mc_info_dict:
            mc = schedule.add_machine(item["mc_id"])
            for key, value in item.items():
                mc.add_contents(key, value)
    ###
    ### Add jobs
    ###
    job_info_fname = input_dict["file_info"]["job_info"]
    with open(
        proj_folder + "\\" + job_info_fname, "r", encoding="utf-8"
    ) as file_data:
        job_info_dict = csv.DictReader(file_data)
        for item in job_info_dict:
            job = schedule.add_job(item["job_id"])
            for key, value in item.items():
                job.add_contents(key, value)

    ###
    ### Add activities
    ###
    ac_info_fname = input_dict["file_info"]["activity_info"]
    core_entity_list = ["mc_id", "ac_type", "job_id", "start", "end"]
    with open(
        proj_folder + "\\" + ac_info_fname, "r", encoding="utf-8"
    ) as file_data:
        ac_info_dict = csv.DictReader(file_data)
        for item in ac_info_dict:
            mc_id = item["mc_id"]
            ac_type = item["ac_type"]
            job_id = item["job_id"]
            start = dt_parse(item["start"])
            end = dt_parse(item["end"])

            if ac_type == ac_types.operation:
                ac = schedule.add_operation(mc_id, job_id, start, end)
            elif ac_type == ac_types.breakdown:
                ac = schedule.add_breakdown(mc_id, start, end)
            for key, value in item.items():
                if key in core_entity_list:
                    continue
                ac.add_contents(key, value)
    return schedule


def main():
    from mstk.test import sample_proj_folder

    read_schedule(sample_proj_folder)


if __name__ == "__main__":
    main()
