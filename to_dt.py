"""moment to datetime.datetime function
Created at 10th Aug. 2020
"""
import datetime as dt


def to_dt_datetime(moment) -> dt.datetime:
    """if moment is not datetime.datetime, convert to datetime.datetime

    Args:
        moment ([type]): datetime.datetime instance or numeric

    Returns:
        datetime.datetime
    """
    if isinstance(moment, dt.datetime):
        return moment
    return dt.datetime.fromtimestamp(moment)
