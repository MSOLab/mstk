from typing import List, Dict, Iterator

from mstk.schedule.schedule import Schedule
from mstk.visualize.color_map import Cmap

import matplotlib
from matplotlib import pyplot as plt
from matplotlib.collections import PatchCollection
import matplotlib.patches as patches
import matplotlib.dates as mdates

from natsort import natsorted

matplotlib.use("Qt5Agg")


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
        self.ac_patch_list: List[str] = []
        self.ac_color_list: List[str] = []

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

        # TODO: change colors according to the properties
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

                ac_patch = patches.Rectangle(
                    (start, 1.1 * target_mc_index),
                    proc,
                    1,
                    facecolor=face_color,
                )
                ac_patch.ac = ac
                self.ac_patch_list += [ac_patch]
                color_id += 1

        patch_collection = PatchCollection(
            self.ac_patch_list, match_original=True
        )
        self.ax_main.add_collection(patch_collection)


def main():

    from mstk.test import sample_proj_folder
    from mstk.visualize.read_schedule import read_schedule

    test_schedule = read_schedule(sample_proj_folder)

    plt_schedule = PlotSchedule(test_schedule)
    plt_schedule.draw_Gantt()
    plt.show()


if __name__ == "__main__":
    main()
