import csv
import datetime as dt

from interval import Interval
from mc_schedule import MCSchedule
from ac_types import AcTypes
from activity import Activity
from schedule import Schedule, MCInfoEssential


def read_data(filename, horizon):

    # from to_dt import to_dt_datetime
    # from datetime.datetime import strptime
    dt_format = "%m/%d/%Y %H:%M"
    ac_types = AcTypes("ac_types.json", "utf-8", True, True)
    # horizon_start = dt.datetime.strptime("7/6/2020 00:00", dt_format)
    # horizon_end = dt.datetime.strptime("7/10/2020 06:00", dt_format)
    # horizon = Interval(horizon_start, horizon_end)
    test_schedule = Schedule("test schedule", horizon, ac_types)
    with open(filename, "r") as _inputfile:
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

    return test_schedule


def main():
    test_schedule = read_data("test_schedule.csv")
    for mc_sched in test_schedule.mc_iter():
        for ac in mc_sched.ac_iter():
            print(ac)


if __name__ == "__main__":
    main()
