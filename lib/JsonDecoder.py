import json
import datetime

DATETIME_FORMAT = u'{0.month:02d}/{0.day:02d}/{0.year:04d} '\
    u'{0.hour:02d}:{0.minute:02d}:{0.second:02d}'


class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return DATETIME_FORMAT.format(obj)
        return json.JSONEncoder.default(
            self, obj
        )

