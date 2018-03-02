import struct
import datetime


def get_datetime_64(raw_timestamp):
    timestamp = struct.unpack("Q", raw_timestamp)[0]

    if timestamp < 0:
        return None

    micro_secs, _ = divmod(timestamp, 10)
    time_delta = datetime.timedelta(
        microseconds=micro_secs
    )

    orig_datetime = datetime.datetime(1601, 1, 1)
    new_datetime = orig_datetime + time_delta

    return new_datetime
