from typing import List, Dict, Iterator
from schedule import Schedule
import matplotlib
from matplotlib import pyplot as plt
import matplotlib.patches as patches
import matplotlib.dates as mdates
import matplotlib.gridspec as gridspec
from natsort import natsorted

my_cmap = [
    "#e6194B",
    "#3cb44b",
    "#ffe119",
    "#4363d8",
    "#f58231",
    "#911eb4",
    "#42d4f4",
    "#f032e6",
    "#bfef45",
    "#fabed4",
    "#469990",
    "#dcbeff",
    "#9A6324",
    "#fffac8",
    "#800000",
    "#aaffc3",
    "#808000",
    "#ffd8b1",
    "#000075",
    "#a9a9a9",
]
my_font_cmap = [
    "#ffffff",
    "#ffffff",
    "#000000",
    "#ffffff",
    "#ffffff",
    "#ffffff",
    "#000000",
    "#ffffff",
    "#000000",
    "#000000",
    "#ffffff",
    "#000000",
    "#ffffff",
    "#000000",
    "#ffffff",
    "#000000",
    "#ffffff",
    "#000000",
    "#ffffff",
    "#ffffff",
]


class PlotSchedule:
    def __init__(self, schedule: Schedule, option: str):
        self.schedule = schedule
        self.option = option
        self.mc_list = natsorted(schedule.mc_schedule_dict.keys())
        self.fig = plt.figure(figsize=(20, len(self.mc_list) * 0.4))
        if option == "interactive":
            self.create_interactive_form()
        elif option == "save":
            self.create_saveplot_form()
        else:
            raise ValueError(
                f'Plot option {option} is not supported -- try ["interactive", "save"]'
            )
        self.format_ax_main()

        self.act_patch_list = []

    def create_saveplot_form(self):
        # TODO: separate interactive plot from the printing version
        gs = self.fig.add_gridspec(
            nrows=1, ncols=2, width_ratios=[4, 1], wspace=0.1, hspace=0.1,
        )
        self.ax_main = self.fig.add_subplot(gs[0, 0])
        self.ax_job_info = self.fig.add_subplot(gs[0, 1])

        # remove ticks in
        for ax in [self.ax_main, self.ax_job_info]:
            ax.set_yticks([])
            if ax != self.ax_main:
                ax.set_xticks([])

    def create_interactive_form(self):
        # TODO: separate interactive plot from the printing version
        gs = self.fig.add_gridspec(
            nrows=2,
            ncols=3,
            height_ratios=[4, 1],
            width_ratios=[1, 4, 1],
            wspace=0.1,
            hspace=0.1,
        )
        self.ax_mc_info = self.fig.add_subplot(gs[0, 0])
        self.ax_main = self.fig.add_subplot(gs[0, 1])
        self.ax_job_info = self.fig.add_subplot(gs[0, 2])
        self.ax_dashboard = self.fig.add_subplot(gs[1, :])

        # remove ticks in
        for ax in [
            self.ax_mc_info,
            self.ax_main,
            self.ax_job_info,
            self.ax_dashboard,
        ]:
            ax.set_yticks([])
            if ax != self.ax_main:
                ax.set_xticks([])

    def format_ax_main(self):
        # set limits in ax_main
        self.x_min = mdates.date2num(self.schedule.horizon.start)
        self.x_max = mdates.date2num(self.schedule.horizon.end)
        self.ax_main.set_xlim(self.x_min, self.x_max)
        self.ax_main.set_ylim(0, len(self.mc_list) * 1.1)

        # set x_axis in datetime format
        locator = mdates.AutoDateLocator(minticks=4)
        formatter = mdates.AutoDateFormatter(locator)
        # formatter = mdates.MinuteLocator
        self.ax_main.xaxis.set_major_locator(locator)
        self.ax_main.xaxis.set_major_formatter(formatter)

    def draw_Gantt(self):
        # Draw machine index in text
        for target_mc_id in self.mc_list:
            mc_index = self.mc_list.index(target_mc_id)
            self.ax_main.text(
                -0.01,
                (2 * mc_index + 1) / 2 / len(self.mc_list),
                target_mc_id,
                ha="right",
                va="center",
                fontsize=14,
                color="k",
                transform=self.ax_main.transAxes,
            )

        # Draw activities
        for target_mc_id in self.mc_list:
            target_mc_index = self.mc_list.index(target_mc_id)
            target_mc_schedule = self.schedule.mc_schedule_dict[target_mc_id]
            for ac in target_mc_schedule.ac_iter():
                # if ac.ac_type == self.schedule.ac_types.idle:
                #     continue

                start = mdates.date2num(ac.interval.start)
                end = mdates.date2num(ac.interval.end)
                proc = end - start

                # TODO: pick colors according to
                face_color = my_cmap[0]
                font_color = my_font_cmap[0]
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
                # act_text =


def main():
    from read_test_schedule import read_data
    from interval import Interval
    import datetime as dt

    dt_format = "%m/%d/%Y %H:%M"

    horizon_start = dt.datetime.strptime("7/6/2020 00:00", dt_format)
    horizon_end = dt.datetime.strptime("7/11/2020 00:00", dt_format)
    horizon = Interval(horizon_start, horizon_end)

    test_schedule = read_data("test_scheduling.csv", horizon)
    plt_schedule = PlotSchedule(test_schedule, "interactive")
    plt_schedule.draw_Gantt()
    plt.show()

    plt_schedule = PlotSchedule(test_schedule, "save")
    plt_schedule.draw_Gantt()
    plt.show()


if __name__ == "__main__":
    main()
