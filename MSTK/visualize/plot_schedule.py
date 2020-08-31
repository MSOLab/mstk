from typing import List, Dict, Iterator
from mstk.schedule.schedule import Schedule
import matplotlib
from matplotlib import pyplot as plt
import matplotlib.patches as patches
import matplotlib.dates as mdates
import matplotlib.gridspec as gridspec
from natsort import natsorted
from mstk.visualize.color_map import Cmap


class PlotSchedule:
    """The test version of schedule drawing (using matplotlib)
    Later, the forms in this class are to be implemented in a PyQt5 form
    """

    def __init__(self, schedule: Schedule):
        self.schedule = schedule
        self.mc_id_list = natsorted(schedule.mc_id_list)
        self.fig = plt.figure(
            figsize=(20, len(self.schedule.mc_id_list) * 0.4)
        )
        self.ax_main = self.fig.add_subplot()

        self.format_ax_main()
        self.cmap = Cmap()
        self.act_patch_list: List[str] = []

    # TODO: implement sorting options for machines

    def format_ax_main(self):
        # set limits in ax_main
        self.x_min = mdates.date2num(self.schedule.horizon.start)
        self.x_max = mdates.date2num(self.schedule.horizon.end)
        self.ax_main.set_xlim(self.x_min, self.x_max)

        # set x_axis in datetime format
        locator = mdates.AutoDateLocator(minticks=4)
        formatter = mdates.AutoDateFormatter(locator)
        # formatter = mdates.MinuteLocator
        self.ax_main.xaxis.set_major_locator(locator)
        self.ax_main.xaxis.set_major_formatter(formatter)
        n = len(self.mc_id_list)
        self.ax_main.set_ylim(0, n * 1.1)
        self.ax_main.set_yticks([1.1 * i + 0.55 for i in range(n)])
        self.ax_main.set_yticklabels(self.mc_id_list)

    def draw_Gantt(self):

        # Draw activities
        color_id = 0

        for target_mc_id in self.mc_id_list:
            target_mc_index = self.mc_id_list.index(target_mc_id)
            target_mc_schedule = self.schedule.mc_dict[
                target_mc_id
            ].mc_schedule
            for ac in target_mc_schedule.ac_iter():
                if ac.ac_type == self.schedule.ac_types.idle:
                    continue

                start = mdates.date2num(ac.interval.start)
                end = mdates.date2num(ac.interval.end)
                proc = end - start

                (face_color, font_color) = self.cmap.material_cmap(color_id)

                alpha_value = 0.8
                if ac.ac_type == self.schedule.ac_types.idle:
                    face_color = "k"
                    alpha_value = 0.1

                act_patch = patches.Rectangle(
                    (start, 1.1 * target_mc_index),
                    proc,
                    1,
                    facecolor=face_color,
                    alpha=alpha_value,
                )
                self.ax_main.add_patch(act_patch)
                color_id += 1


def main():
    import csv
    import datetime as dt
    from mstk.schedule.ac_types import AcTypes
    from mstk.schedule.interval import Interval
    from mstk.schedule.machine import Machine
    from mstk.schedule.activity import Activity

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
        # with open("test/test_schedule.csv", "r") as _inputfile:
        job_list = list(csv.reader(_inputfile))[1:]
    # print(job_list)
    # create machine list
    machine_list = []
    for job in job_list:
        mc_id = job[1]
        if mc_id not in machine_list:
            machine_list += [mc_id]
            # mc_info = MCInfoEssential(mc_id)
            test_schedule.add_machine(mc_id)

    # create job list
    for job in job_list:
        mc_id = job[1]
        start = dt.datetime.strptime(job[2], dt_format)
        end = dt.datetime.strptime(job[3], dt_format)
        job_info = job[4]
        test_schedule.add_operation_to_mc(mc_id, start, end)

    plt_schedule = PlotSchedule(test_schedule)
    plt_schedule.draw_Gantt()
    plt.show()


if __name__ == "__main__":
    main()
