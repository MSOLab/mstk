"""moment to datetime.datetime function
Created on 10th Aug. 2020
"""
import datetime as dt
from typing import Union

__all__ = ["to_dt_datetime"]


class Moment:
    """A container for time-related object (e.g. dt.datetime, int, ...)

    Warning:
        Not implemented
    """

    __slots__ = ["__value"]

    def __init__(self, value):
        raise NotImplementedError("Moment is not supported")


def to_dt_datetime(moment: Union[int, dt.datetime]) -> dt.datetime:
    """if moment is an integer, convert to datetime.datetime

    Args:
        moment (Union[int, datetime.datetime])
            numeric or datetime.datetime instance

    Raises:
        TypeError: if unsupported type is given

    Returns:
        datetime.datetime
    """
    if isinstance(moment, dt.datetime):
        return moment
    elif isinstance(moment, int) or isinstance(moment, float):
        # elif moment.isnumeric():
        return dt.datetime.fromtimestamp(moment)
    else:
        raise TypeError(
            f"moment [{moment}] of type {type(moment)} is not supported"
        )


def main():
    print(to_dt_datetime(1))
    print(to_dt_datetime(dt.datetime(2020, 8, 10)))
    try:
        to_dt_datetime("aa")
    except Exception as e:
        print("## (Intended) ", e)


if __name__ == "__main__":
    main()
