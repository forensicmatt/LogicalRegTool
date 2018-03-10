import struct
import logging
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


def extract_tsk_file_temp(file_info, temp_file_io):
    offset = 0
    size = file_info['tsk_file'].info.meta.size
    BUFF_SIZE = 1024 * 1024

    while offset < size:
        available_to_read = min(BUFF_SIZE, size - offset)
        data = file_info['tsk_file'].read_random(
            offset, available_to_read
        )
        if not data:
            break

        offset += len(data)
        temp_file_io.write(data)

    temp_file_io.close()
    logging.debug(u"{} -> {}".format(file_info['fullname'], temp_file_io.name))