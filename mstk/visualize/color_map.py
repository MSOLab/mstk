""" a class for colormap
Created at 30th Aug. 2020
"""

from typing import List, Tuple

import json
import os

__all__ = ["Cmap"]
current_path = os.path.dirname(os.path.abspath(__file__))


class Cmap:
    """A class for default colormaps
    """

    def __init__(
        self,
        encoding: str = f"utf-8",
        filename=f"{current_path}/color_map.json",
    ):
        self.all_types: List[str] = list()
        with open(filename, encoding=encoding) as file_data:
            input_dict = json.load(file_data)
            for key, value in input_dict.items():
                self.all_types.append(value)
                self.__dict__[key] = value

    def simple_cmap(self, index: int) -> Tuple[str, str]:
        """Selects a color among 20 colors from https://sashamaps.net/docs/resources/20-colors/

        Args:
            index (int): index for the color

        Returns:
            Tuple[str, str]: [color (in hex), font (in hex)]
        """
        cmap = self.__dict__["simple"]
        num_color = len(cmap["cmap"])
        return (
            cmap["cmap"][index % num_color],
            cmap["fontmap"][index % num_color],
        )

    def material_cmap(self, index: int) -> Tuple[str, str]:
        """Selects a color using material design colormap with 14 sets (9 levels in each)

        Order of colors from: https://sashamaps.net/docs/resources/20-colors/

        Args:
            index (int): index for the color

        Returns:
            Tuple[str, str]: [color (in hex), font (in hex)]
        """
        color_list = [
            "red",
            "green",
            "yellow",
            "blue",
            "purple",
            "cyan",
            "pink",
            "teal",
            "brown",
            "light_blue",
            "indigo",
            "blue_grey",
        ]
        num_color = len(color_list)  # number of cmaps to use
        len_color = len(
            self.__dict__[color_list[0]]["cmap"]
        )  # number of colors in each cmap

        new_index = index % (num_color * len_color)
        q = int(new_index / num_color)
        r = new_index % num_color

        cmap = self.__dict__[color_list[r]]["cmap"]
        fontmap = self.__dict__[color_list[r]]["fontmap"]
        return (cmap[q], fontmap[q])


def main():
    cmap = Cmap()
    for i in range(300):
        print(i, cmap.material_cmap(i))
    for i in range(50):
        print(i, cmap.simple_cmap(i))


if __name__ == "__main__":
    main()
