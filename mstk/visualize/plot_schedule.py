__all__ = ["PlotSchedule"]
from typing import List, Dict, Iterator, Callable, Any

import matplotlib
from matplotlib import pyplot as plt
from matplotlib.collections import PatchCollection, LineCollection
import matplotlib.patches as patches
import matplotlib.dates as mdates
import matplotlib.lines as lines

from mstk.schedule.schedule import Schedule
from mstk.visualize.color_map import Cmap


class PlotSchedule:
    """A prototype version of schedule drawing (using matplotlib)

    Later, the methods in this class are to be implemented concordant to PyQt5
    """

    def __init__(self, schedule: Schedule, **kwargs):

        self.__schedule: Schedule = schedule
        self.__mc_id_list: List[str] = [mc_id for mc_id in schedule.mc_id_list]
        self.__mc_id_list.reverse()
        self.__job_id_list: List[str] = [
            job_id for job_id in schedule.job_id_list
        ]

        self.cmap = Cmap()
        self.__legend_patch_list: List[patches.Rectangle] = []
        self.__horz_line_list: List[lines.Line2D] = []
        self.__operation_patch_list: List[patches.Rectangle] = []
        self.__breakdown_patch_list: List[patches.Rectangle] = []

        # **kwargs
        self.legend_on = kwargs["legend_on"] if "legend_on" in kwargs else True
        self.horz_line_on = (
            kwargs["horz_line_on"] if "horz_line_on" in kwargs else False
        )

    @property
    def schedule(self) -> Schedule:
        return self.__schedule

    @property
    def mc_id_list(self) -> List[str]:
        return self.__mc_id_list

    @property
    def job_id_list(self) -> List[str]:
        return self.__job_id_list

    @property
    def horz_line_list(self) -> List[lines.Line2D]:
        return self.__horz_line_list

    @property
    def legend_patch_list(self) -> List[patches.Rectangle]:
        return self.__legend_patch_list

    @property
    def operation_patch_list(self) -> List[patches.Rectangle]:
        return self.__operation_patch_list

    @property
    def breakdown_patch_list(self) -> List[patches.Rectangle]:
        return self.__breakdown_patch_list

    def sort_mc_id_list(
        self, func: Callable[[str], Any], reverse: bool = False
    ):
        """Sorts the mc_id_list according to values of func(mc_id)

        Args:
            func (Callable[[str], Any]): a key generator
            reverse (bool, optional): whether to sort in a descending order. Defaults to False.
        """

        self.__mc_id_list.sort(key=func, reverse=reverse)

    def sort_job_id_list(
        self, func: Callable[[str], Any], reverse: bool = False
    ):
        self.__job_id_list.sort(key=func, reverse=reverse)

        """Sorts the job_id_list according to values of func(mc_id)

        Args:
            func (Callable[[str], Any]): a key generator
            reverse (bool, optional): whether to sort in a descending order. Defaults to False.
        """

    def reset_figure(self):
        """Initializes figure, axis, and patch lists"""
        self.fig = plt.figure(
            figsize=(20, len(self.schedule.mc_id_list) * 0.4)
        )
        self.ax_main = self.fig.add_subplot()
        self.ax_main.set_title(f"{self.schedule.schedule_id}")

        self.format_ax_main()

        self.__horz_line_list = []
        self.__legend_patch_list = []
        self.__operation_patch_list = []
        self.__breakdown_patch_list = []

    def format_ax_main(self):
        """Sets the main axis of a figure"""
        # set limits in ax_main
        self.x_min = mdates.date2num(self.schedule.horizon.start)
        self.x_max = mdates.date2num(self.schedule.horizon.end)
        self.ax_main.set_xlim(self.x_min, self.x_max)

        # set x_axis in datetime format
        locator = mdates.AutoDateLocator(minticks=4)
        formatter = mdates.AutoDateFormatter(locator)

        self.ax_main.xaxis.set_major_locator(locator)
        self.ax_main.xaxis.set_major_formatter(formatter)
        n = len(self.mc_id_list)
        self.ax_main.set_ylim(0, n * 1.1)
        self.ax_main.set_yticks([1.1 * i + 0.55 for i in range(n)])
        self.ax_main.set_yticklabels(self.mc_id_list)

    def draw_legend(self):
        """Draw legends on the second windows"""
        job_list = self.job_id_list
        ncol = int(len(job_list) / 20) + 1

        self.fig_legend = plt.figure(figsize=(ncol * 1.4, 4), frameon=False)
        self.ax_legend = self.fig_legend.add_subplot()

        self.__legend_patch_list = []
        for job_id in job_list:
            color_id = job_list.index(job_id)
            face_color = self.cmap.material_cmap(color_id)[0]
            legend_patch = patches.Rectangle(
                (0, 0), 0, 0, facecolor=face_color, alpha=1, label=job_id
            )
            self.legend_patch_list.append(legend_patch)
            self.ax_legend.add_patch(legend_patch)

        self.ax_legend.legend(ncol=ncol, loc="upper left")
        self.ax_legend.axis("off")

        def on_patch_click(event):
            """Triggers displaying contents for clicked objects

            Args:
                event (matplotlib.backend_bases.MouseEvent): a mouse click event
            """
            for legend_handle in self.ax_legend.legend_.legendHandles:
                cont, ind = legend_handle.contains(event)
                if cont:
                    job_id = legend_handle._label
                    self.schedule.job_dict[job_id].display_contents(print)

        self.fig_legend.canvas.mpl_connect(
            "button_press_event", on_patch_click
        )

        self.fig_legend.tight_layout()

    def draw_horz_line(self):
        """Draws horizontal lines to divide neiboring schedules"""
        for target_mc_index, target_mc_id in enumerate(self.mc_id_list):
            height = 1.1 * target_mc_index
            self.horz_line_list += [
                [(self.x_min, height), (self.x_max, height)]
            ]
        self.horz_line_collection = LineCollection(
            self.horz_line_list, colors=["k"], linewidth=0.7
        )
        self.ax_main.add_collection(self.horz_line_collection)

    def generate_overlay_schedule(self, overlay_schedule: Schedule):
        """Generates a patch collection to overlay

        Args:
            overlay_schedule (Schedule): a schedule to overlay

        Returns:
            matplotlib.collections.PatchCollection: a collection of the trimmed patches

        """
        overlay_patch_list: List[patches] = []

        def patch_generator(overlay_schedule: Schedule):
            """Generates trimmed patches of overlay_schedule according to the new horizon

            Args:
                overlay_schedule (Schedule): A schedule to overlay

            Yields:
                matplotlib.patches.Rectangle: a patch of the trimmed activity
            """
            for mc_id, mc in overlay_schedule.mc_dict.items():
                if mc_id not in self.mc_id_list:
                    continue
                target_mc_index = self.mc_id_list.index(mc_id)
                for ac in mc.actual_ac_iter():
                    new_interval = self.schedule.transform_interval_to_horizon(
                        ac.interval, self.schedule.horizon, "trim"
                    )
                    if new_interval == None:
                        continue
                    start = mdates.date2num(new_interval.start)
                    end = mdates.date2num(new_interval.end)
                    proc = end - start
                    ac_patch = patches.Rectangle(
                        (start, 1.1 * target_mc_index),
                        proc,
                        1,
                        facecolor="k",
                        edgecolor="r",
                        alpha=0.3,
                        linewidth=2,
                    )
                    yield ac_patch

        overlay_patch_list += [
            patch for patch in patch_generator(overlay_schedule)
        ]

        return PatchCollection(
            overlay_patch_list, match_original=True, hatch="///"
        )

    def draw_Gantt(self, export_fname: str = None, **kwargs):
        """Draws a Gantt chart of self.schedule

        Args:
            export_fname (str, optional):  a file name to export (Default: **None** to enter an interactive mode)
        """

        # TODO: change color maps according to various operation properties
        self.reset_figure()

        job_list = self.schedule.job_id_list
        for target_mc_index, target_mc_id in enumerate(self.mc_id_list):
            target_mc_schedule = self.schedule.mc_dict[
                target_mc_id
            ].mc_schedule

            for ac in target_mc_schedule.actual_ac_iter():

                start = mdates.date2num(ac.interval.start)
                end = mdates.date2num(ac.interval.end)
                proc = end - start

                if ac.ac_type == self.schedule.ac_types_param.operation:
                    job_id = job_list.index(ac.job.job_id)
                    face_color = self.cmap.material_cmap(job_id)[0]
                    ac_patch = patches.Rectangle(
                        (start, 1.1 * target_mc_index),
                        proc,
                        1,
                        facecolor=face_color,
                    )
                    self.operation_patch_list.append(ac_patch)

                if ac.ac_type == self.schedule.ac_types_param.breakdown:
                    face_color = "#ffebee"
                    edge_color = "k"
                    linestyle = "--"

                    ac_patch = patches.Rectangle(
                        (start, 1.1 * target_mc_index),
                        proc,
                        1,
                        facecolor=face_color,
                        edgecolor=edge_color,
                        linestyle=linestyle,
                    )
                    self.breakdown_patch_list.append(ac_patch)

                ac_patch.ac = ac

        ### PatchCollection for efficient rendering
        self.operation_patch_collection = PatchCollection(
            self.operation_patch_list, match_original=True
        )
        self.ax_main.add_collection(self.operation_patch_collection)

        self.breakdown_patch_collection = PatchCollection(
            self.breakdown_patch_list, match_original=True, hatch="\\\\\\"
        )
        self.ax_main.add_collection(self.breakdown_patch_collection)

        if "overlay_schedule" in kwargs:
            overlay_schedule = kwargs["overlay_schedule"]
            self.ax_main.add_collection(
                self.generate_overlay_schedule(overlay_schedule)
            )

        def on_patch_click(event):
            """Triggers displaying contents for clicked objects

            Args:
                event (matplotlib.backend_bases.MouseEvent): a mouse click event
            """
            for tick in self.ax_main.yaxis.majorTicks:
                cont, ind = tick.label.contains(event)
                if cont:
                    mc = self.schedule.mc_dict[tick.label._text]
                    mc.display_contents(print)
                    return

            cont, ind = self.operation_patch_collection.contains(event)
            if cont:
                index = ind["ind"][0]
                ac = self.operation_patch_list[index].ac
                ac.display_contents(print)
                return

            cont, ind = self.breakdown_patch_collection.contains(event)
            if cont:
                index = ind["ind"][0]
                ac = self.breakdown_patch_list[index].ac
                ac.display_contents(print)
                return

        self.fig.canvas.mpl_connect("button_press_event", on_patch_click)
        if self.legend_on == True:
            self.draw_legend()
        if self.horz_line_on == True:
            self.draw_horz_line()
        if export_fname == None:
            plt.show()
        else:
            self.fig.savefig(export_fname, dpi=150)


def main():
    from datetime import datetime
    from mstk.test import sample_proj_folder
    from mstk.read_schedule import read_schedule

    test_schedule = read_schedule(sample_proj_folder)
    new_schedule = test_schedule.transform(
        f"copy of {test_schedule.schedule_id}",
        start=datetime(2020, 1, 1, 14),
        end=datetime(2020, 1, 3, 11),
        horz_overlap="trim",
    )
    plot_option = {"legend_on": True, "horz_line_on": False}
    plt_schedule = PlotSchedule(test_schedule, **plot_option)
    plt_schedule.draw_Gantt(overlay_schedule=new_schedule)
    plt_schedule.sort_job_id_list(str, reverse=True)
    plt_schedule.draw_Gantt(overlay_schedule=new_schedule)


if __name__ == "__main__":
    main()
