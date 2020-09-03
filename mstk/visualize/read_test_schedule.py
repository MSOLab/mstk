import csv
import datetime as dt

from mstk.schedule.interval import Interval

# from mstk.schedule.mc_schedule import MCSchedule
from mstk.schedule.schedule import Schedule
from mstk.schedule.ac_types import AcTypes
from mstk.schedule.activity import Activity

# from mstk.schedule.schedule import Schedule, MCInfoEssential


def read_data(filename, horizon):

    dt_format = "%m/%d/%Y %H:%M"
    ac_types = AcTypes("utf-8", True, True)

    test_schedule = Schedule("test schedule", horizon, ac_types)
    with open(filename, "r") as _inputfile:
        oper_list = list(csv.reader(_inputfile))[1:]

    # # create machine list
    # machine_list = []
    # for job in job_list:
    #     mc_id = job[1]
    #     if mc_id not in machine_list:
    #         machine_list += [mc_id]
    #         mc_info = MCInfoEssential(mc_id)
    #         test_schedule.add_machine(mc_info)

    # # create job list
    # for job in job_list:
    #     mc_id = job[1]
    #     start = dt.datetime.strptime(job[2], dt_format)
    #     end = dt.datetime.strptime(job[3], dt_format)
    #     job_info = job[4]
    #     test_schedule.add_operation_to_mc(mc_id, job_info, start, end)

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

    return test_schedule


def main():
    test_schedule = read_data("D:/Projects/MSTK/mstk/test/test_schedule.csv")
    for mc_sched in test_schedule.mc_iter():
        for ac in mc_sched.ac_iter():
            print(ac)


if __name__ == "__main__":
    main()
