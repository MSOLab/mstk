from typing import List, Dict, Iterator

from mstk.schedule.schedule import Schedule
from mstk.visualize.color_map import Cmap

import matplotlib
from matplotlib import pyplot as plt
from matplotlib.collections import PatchCollection
import matplotlib.patches as patches
import matplotlib.dates as mdates

from natsort import natsorted

# matplotlib.use("Qt5Agg")


class PlotSchedule:
    """The test version of schedule drawing (using matplotlib)
    Later, the forms in this class are to be implemented in a PyQt5 form
    """

    def __init__(self, schedule: Schedule, **kwargs):
        self.schedule = schedule
        self.mc_id_list = natsorted(schedule.mc_id_list)
        self.mc_id_list.reverse()
        self.job_id_list = natsorted(schedule.job_id_list)

        self.fig = plt.figure(
            figsize=(20, len(self.schedule.mc_id_list) * 0.4)
        )
        self.ax_main = self.fig.add_subplot()
        self.ax_main.set_title(f"{self.schedule.schedule_id}")
        self.format_ax_main()
        self.cmap = Cmap()
        self.ac_patch_list: List[str] = []
        self.ac_color_list: List[str] = []

        if "legend_on" in kwargs:
            self.legend_on = kwargs["legend_on"]
        else:
            self.legend_on = True

    # TODO: implement sorting options for machines
    # TODO: Add option for drawing horizontal lines
    # TODO: Add legends option

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

    def draw_legend(self):
        # TODO: Show the legend in another window using PyQt5
        job_list = self.job_id_list
        ncol = int(len(job_list) / 20) + 1

        self.fig_legend = plt.figure(figsize=(ncol * 1.4, 4), frameon=False)
        self.ax_legend = self.fig_legend.add_subplot()

        self.legend_patch_list = []
        for job_id in job_list:
            color_id = job_list.index(job_id)
            face_color = self.cmap.material_cmap(color_id)[0]
            legend_patch = patches.Rectangle(
                (0, 0), 0, 0, facecolor=face_color, alpha=1, label=job_id
            )
            self.legend_patch_list += [legend_patch]
            self.ax_legend.add_patch(legend_patch)
        # self.legend_patch_collection = PatchCollection(
        #     self.legend_patch_list, match_original=True
        # )
        # self.ax_legend.add_collection(self.legend_patch_collection)
        self.ax_legend.legend(ncol=ncol, loc="upper left")
        self.ax_legend.axis("off")
        self.fig_legend.canvas.toolbar.pack_forget()
        self.fig_legend.tight_layout()

    def draw_Gantt(self):

        # Draw activities

        # TODO: change colors according to the properties
        job_list = self.schedule.job_id_list
        for target_mc_index, target_mc_id in enumerate(self.mc_id_list):
            # target_mc_index = self.mc_id_list.index(target_mc_id)
            target_mc_schedule = self.schedule.mc_dict[
                target_mc_id
            ].mc_schedule
            for ac in target_mc_schedule.ac_iter():
                if ac.ac_type == self.schedule.ac_types.idle:
                    continue

                start = mdates.date2num(ac.interval.start)
                end = mdates.date2num(ac.interval.end)
                proc = end - start

                # (face_color, font_color) = self.cmap.material_cmap(color_id)
                alpha_value = 1
                edge_color = None
                linestyle = None
                # linewidth = None
                if ac.ac_type == self.schedule.ac_types.operation:
                    job_id = job_list.index(ac.job.job_id)
                    face_color = self.cmap.material_cmap(job_id)[0]
                if ac.ac_type == self.schedule.ac_types.idle:
                    face_color = "k"
                    alpha_value = 0.1
                if ac.ac_type == self.schedule.ac_types.breakdown:
                    face_color = "#ffebee"
                    edge_color = "k"
                    linestyle = "--"

                ac_patch = patches.Rectangle(
                    (start, 1.1 * target_mc_index),
                    proc,
                    1,
                    facecolor=face_color,
                    alpha=alpha_value,
                    edgecolor=edge_color,
                    linestyle=linestyle,
                )

                ac_patch.ac = ac

                self.ac_patch_list += [ac_patch]
                # self.ax_main.add_patch(ac_patch)

        ### PatchCollection for efficient rendering
        self.patch_collection = PatchCollection(
            self.ac_patch_list, match_original=True
        )
        self.ax_main.add_collection(self.patch_collection)

        def on_patch_click(event):

            cont, ind = self.patch_collection.contains(event)
            if cont:
                index = ind["ind"][0]
                # TODO: implement print function for each activity type
                print(self.ac_patch_list[index].ac.job.job_id)

        self.fig.canvas.mpl_connect("button_press_event", on_patch_click)
        if self.legend_on == True:
            self.draw_legend()
        plt.show()


def main():

    from mstk.test import sample_proj_folder
    from mstk.visualize.read_schedule import read_schedule

    test_schedule = read_schedule(sample_proj_folder)
    plot_option = {"legend_on": False}
    plt_schedule = PlotSchedule(test_schedule, **plot_option)
    plt_schedule.draw_Gantt()
    plt.show()


if __name__ == "__main__":
    main()
