"""activity type definition class
Created at 10th Aug. 2020
"""

__all__ = [AcTypesParam]

import json
from typing import List
import os

current_path = os.path.dirname(os.path.abspath(__file__))


class AcTypesParam:
    """A container class for activity types

    Reads .json file to initialize (default keys: [idle, operation, setup, breakdown])

    Each type contains a prefix(str) used in naming activities

    :raises ValueError: if 'idle' is not in the keys

    """

    idle: str
    operation: str
    setup: str
    breakdown: str

    def __init__(
        self,
        encoding: str = "utf-8",
        filename: str = f"{current_path}/default.json",
    ):
        self.all_types: List[str] = list()
        with open(filename, encoding=encoding) as file_data:
            input_dict = json.load(file_data)
            for key, value in input_dict.items():
                if key == "_comment":
                    continue
                self.all_types.append(value)
                self.__dict__[key] = value
        if "idle" not in self.__dict__:
            raise ValueError("Type 'idle' and its display prefix should exist")

    def is_idle(self, given_type: str) -> bool:
        if given_type == self.idle:
            return True
        return False

    def is_operation(self, given_type: str) -> bool:
        if given_type == self.operation:
            return True
        return False

    def is_setup(self, given_type: str) -> bool:
        if given_type == self.setup:
            return True
        return False

    def is_breakdown(self, given_type: str) -> bool:
        if given_type == self.breakdown:
            return True
        return False


def main():
    ac_types = AcTypesParam()
    print("Finished")


if __name__ == "__main__":
    main()
