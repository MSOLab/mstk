from typing import List, Dict, Iterator
from schedule import Schedule
import matplotlib
from matplotlib import pyplot as plt
import matplotlib.patches as patches
import matplotlib.dates as mdates
import matplotlib.gridspec as gridspec
from natsort import natsorted

from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg

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

import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup

from kivy.uix.floatlayout import FloatLayout
from kivy.lang import Builder
from kivy.graphics import Color, Line, Ellipse, Rectangle
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.switch import Switch

# class PltForm(FigureCanvasKivyAgg):
#     pass


def dt_interval_to_int(interval):
    start = interval.start.timestamp()
    end = interval.end.timestamp()

    return (start, end)


class AxisLine(Widget):
    def __init__(self, orientation, **kwargs):
        super().__init__(**kwargs)
        self.active = True
        self.orientation = orientation

    def draw(self):
        # self.canvas.clear()
        with self.canvas:
            # print(axis_canvas)
            Color(0, 0, 0, 1)
            if self.orientation == "x":
                self.axis = Line(
                    points=(
                        self.pos[0],
                        self.pos[1],
                        self.pos[0] + self.width,
                        self.pos[1],
                    ),
                    width=3,
                )
            elif self.orientation == "y":
                self.axis = Line(
                    points=(
                        self.pos[0],
                        self.pos[1],
                        self.pos[0],
                        self.pos[1] + self.height,
                    ),
                    width=3,
                )
            else:
                raise Exception(f"invalid axis orientation {orientation}")

    def redraw(self, *args):
        # self.axis.pos = self.pos
        # self.pos = self.parent.pos
        # self.size = self.parent.size
        print("axis redrawn")
        pos = self.parent.pos
        width = self.parent.width
        height = self.parent.height
        self.canvas.clear()
        with self.canvas:
            # print(axis_canvas)
            Color(0, 0, 0, 1)
            if self.orientation == "x":
                self.axis = Line(
                    points=(pos[0], pos[1], pos[0] + width, pos[1],),
                    width=3,
                )
            elif self.orientation == "y":
                self.axis = Line(
                    points=(pos[0], pos[1], pos[0], pos[1] + height,),
                    width=3,
                )
        # self.axis.size = self.size


class AcButton(ButtonBehavior, BoxLayout):
    def __init__(self, mc_id, ac, **kwargs):
        super().__init__(**kwargs)
        self.mc_id = mc_id
        self.ac = ac
        self.bind(
            pos=self.redraw, size=self.redraw, on_press=self.show_ac_info
        )

    def show_ac_info(self, instance):
        # print(self.mc_id)
        popup = Popup(
            title="Activity info",
            content=Label(
                text=f"{self.ac.ac_id}\n Interval: {self.ac.interval}",
                markup=True,
            ),
            # size=(100, 100),
            size_hint=(0.4, 0.4),
            auto_dismiss=True,
        )
        popup.open()

    def redraw(self, *args):

        self.canvas.before.clear()
        with self.canvas.before:
            if self.ac.ac_type == "Operation_":
                Color(0, 1, 0, 0.3)
            else:
                Color(0, 0, 0, 0.1)
            self.bg = Rectangle(
                pos=self.pos, size=(self.size[0], self.size[1]),
            )

        pass


class MCSchdeduleBox(BoxLayout):
    def __init__(self, mc_id, mc_schedule, num_mc, **kwargs):
        super().__init__(**kwargs)
        self.mc_id = mc_id
        self.mc_schedule = mc_schedule
        self.num_mc = num_mc
        self.orientation = "horizontal"
        self.ac_button_dict = {}
        self.draw()
        self.bind(size=self.resize)

    def draw(self, *args):
        horizon = dt_interval_to_int(self.mc_schedule.horizon)
        self.horz_length = horizon[1] - horizon[0]
        with self.canvas:
            for ac_id in self.mc_schedule.ac_id_list:
                ac = self.mc_schedule.ac_dict[ac_id]
                (ac_start, ac_end) = dt_interval_to_int(ac.interval)
                size_hint_value = (ac_end - ac_start) / self.horz_length

                ac_button = AcButton(
                    self.mc_id,
                    ac,
                    size_hint=(size_hint_value, None),
                    height=self.height,
                )
                self.ac_button_dict[ac.ac_id] = ac_button
                self.add_widget(ac_button)

    def resize(self, *args):
        #     self.canvas.before.clear()
        #     with self.canvas.before:
        #         Color(1, 1, 0, 0.4)
        #         self.bg = Rectangle(pos=self.pos, size=self.size)
        for ac_button in self.ac_button_dict.values():
            ac_button.size = [ac_button.size[0], self.height]


class AxisLayout(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.schedule = App.get_running_app().schedule
        self.mc_list = App.get_running_app().mc_list
        self.mc_schedule_box_dict = {}
        self.ac_button_dict = {}
        self.num_mc = len(self.schedule.mc_id_list)
        self.draw()
        self.bind(size=self.redraw)

    def draw(self):
        self.axis_x = AxisLine("x",)
        self.axis_y = AxisLine("y")
        with self.canvas:
            for mc_id in self.mc_list:
                self.mc_schedule_box_dict[mc_id] = MCSchdeduleBox(
                    mc_id,
                    self.schedule.mc_schedule_dict[mc_id],
                    self.num_mc,
                    size_hint=(None, None),
                )
                self.add_widget(self.mc_schedule_box_dict[mc_id])
            self.add_widget(self.axis_x)
            self.add_widget(self.axis_y)

    def redraw(self, *args):
        print("layout redrawn")

        pos = self.pos
        width = self.width
        height = self.height
        for axis in [self.axis_x, self.axis_y]:
            axis.canvas.clear()
            with axis.canvas:
                Color(0, 0, 0, 1)
                if axis.orientation == "x":
                    axis.axis = Line(
                        points=(
                            pos[0] - 1,
                            pos[1] - 1,
                            pos[0] + width,
                            pos[1] - 1,
                        ),
                        width=1,
                    )
                elif axis.orientation == "y":
                    axis.axis = Line(
                        points=(
                            pos[0] - 1,
                            pos[1] - 1,
                            pos[0] - 1,
                            pos[1] + height,
                        ),
                        width=1,
                    )
        i = 0
        for mc_id in self.mc_list:
            mc_schedule_box = self.mc_schedule_box_dict[mc_id]
            mc_schedule_box.pos = [
                self.pos[0],
                self.pos[1]
                + self.height
                - (1 + i) / self.num_mc * self.height,
            ]
            mc_schedule_box.size = (
                self.size[0],
                self.size[1] / self.num_mc - 2,
            )
            i += 1


class MCButton(Button):
    def __init__(self, mc_id, **kwargs):
        super().__init__(**kwargs)
        self.mc_id = mc_id
        self.text = f"[color=000000]{mc_id}[/color]"
        self.bind(on_press=self.show_mc_info)

    def show_mc_info(self, instance):
        print(self.mc_id)
        popup = Popup(
            title="Machine info",
            content=Label(text=self.mc_id),
            size=(100, 100),
            size_hint=(0.3, 0.3),
            auto_dismiss=True,
        )
        popup.open()


class MachineLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.mc_list = App.get_running_app().mc_list

        self.mc_label_list = {}
        self.draw()

    def draw(self):

        with self.canvas:
            for mc_id in self.mc_list:
                self.mc_label_list[mc_id] = MCButton(
                    mc_id, background_color=(0, 0, 0, 0), markup=True,
                )
                self.add_widget(self.mc_label_list[mc_id])

    pass


class EmptyLayout(BoxLayout):
    pass


class XtickLayout(BoxLayout):
    pass


class PlotArea(BoxLayout):
    pass


class LegendArea(BoxLayout):
    pass


class Dashboard(BoxLayout):
    pass


class MainArea(BoxLayout):
    pass


class Menu_bar(BoxLayout):
    pass


class RootLayout(BoxLayout):
    pass


class SchedApp(App):
    def __init__(self, schedule: Schedule, option: str):
        super().__init__()
        # print(self.ids)
        # def __init__(self, schedule: Schedule, option: str):
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

    def build(self):
        self.root = Builder.load_file("sched.kv")
        plot_layout = self.root.ids["plot"]
        axis_layout = self.root.ids["axis"]

        return self.root

    def create_saveplot_form(self):
        # TODO: separate interactive plot from the printing version
        gs = self.fig.add_gridspec(
            nrows=1, ncols=2, width_ratios=[4, 0], wspace=0.1, hspace=0.1,
        )
        self.ax_main = self.fig.add_subplot(gs[0, 0])
        # self.ax_job_info = self.fig.add_subplot(gs[0, 1])
        # self.ax_main = self.fig.add_subplot()
        # self.ax_main.set_yticks([])
        # remove ticks in
        # for ax in [self.ax_main, self.ax_job_info]:
        for ax in [self.ax_main]:
            ax.set_yticks([])
            if ax != self.ax_main:
                ax.set_xticks([])

        self.draw_Gantt()

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
            target_mc_schedule = self.schedule.mc_schedule_dict[
                target_mc_id
            ]
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

    pass


def main():
    from read_test_schedule import read_data
    from interval import Interval
    import datetime as dt

    # SchedApp().run()
    dt_format = "%m/%d/%Y %H:%M"

    horizon_start = dt.datetime.strptime("7/6/2020 00:00", dt_format)
    horizon_end = dt.datetime.strptime("7/11/2020 00:00", dt_format)
    horizon = Interval(horizon_start, horizon_end)

    test_schedule = read_data("test_scheduling.csv", horizon)
    test_kivy_schedule = SchedApp(test_schedule, "save").run()


if __name__ == "__main__":
    main()
