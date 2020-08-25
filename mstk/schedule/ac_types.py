"""activity type definition class
Created at 10th Aug. 2020
"""
import json
from typing import List


class AcTypes:
    idle: str
    operation: str
    setup: str
    breakdown: str

    def __init__(
        self,
        encoding: str,
        setup_exists: bool,
        breakdown_exists: bool,
        filename="schedule/ac_type_options/default.json",
        # TODO: use **kwargs to change ac_type json file location according to setup / brkdown
    ):
        self.all_types: List[str] = list()
        with open(filename, encoding=encoding) as file_data:
            input_dict = json.load(file_data)
            for key, value in input_dict.items():
                if key == "_comment":
                    continue
                self.all_types.append(value)
                self.__dict__[key] = value
        if not setup_exists:
            self.all_types.remove("setup")
            del self.__dict__["setup"]
        if not breakdown_exists:
            self.all_types.remove("breakdown")
            del self.__dict__["breakdown"]
        if "idle" not in self.__dict__:
            raise ValueError("Type 'idle' and its display prefix should exist")

    def is_idle(self, given_type: str):
        if given_type == self.idle:
            return True
        return False

    def is_operation(self, given_type: str):
        if given_type == self.operation:
            return True
        return False

    def is_setup(self, given_type: str):
        if given_type == self.setup:
            return True
        return False

    def is_breakdown(self, given_type: str):
        if given_type == self.breakdown:
            return True
        return False


def main():

    ac_types = AcTypes("utf-8", True, True)


if __name__ == "__main__":
    main()
