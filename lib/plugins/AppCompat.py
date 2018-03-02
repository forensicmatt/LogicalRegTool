import json
from collections import OrderedDict
from lib.Helpers import get_datetime_64
from lib.JsonDecoder import ComplexEncoder

APP_COMPAT_FLAGS_PERSISTED = [
    u"Software\\Microsoft\\Windows NT\\CurrentVersion\\AppCompatFlags\\Compatibility Assistant\\Persisted",
    u"Wow6432Node\\Software\\Microsoft\\Windows NT\\CurrentVersion\\AppCompatFlags\\Compatibility Assistant\\Persisted",
    u"Microsoft\\Windows NT\\CurrentVersion\\AppCompatFlags\\Compatibility Assistant\\Persisted",
    u"Wow6432Node\\Microsoft\\Windows NT\\CurrentVersion\\AppCompatFlags\\Compatibility Assistant\\Persisted"
]

APP_COMPAT_FLAGS_STORE = [
    u"Software\\Microsoft\\Windows NT\\CurrentVersion\\AppCompatFlags\\Compatibility Assistant\\Store",
    u"Wow6432Node\\Software\\Microsoft\\Windows NT\\CurrentVersion\\AppCompatFlags\\Compatibility Assistant\\Store",
    u"Microsoft\\Windows NT\\CurrentVersion\\AppCompatFlags\\Compatibility Assistant\\Store",
    u"Wow6432Node\\Microsoft\\Windows NT\\CurrentVersion\\AppCompatFlags\\Compatibility Assistant\\Store"
]


class AppCompact(object):
    def __init__(self):
        pass

    def run(self, registry_manager):
        for reg_handler in registry_manager.iter_registry_handlers(name=u'NTUSER.DAT'):
            hive = reg_handler.get_hive()

            for location_path in APP_COMPAT_FLAGS_STORE:
                store_key = hive.find_key(location_path)
                if store_key is not None:
                    for value in store_key.values():
                        value_name = value.name()
                        value_data = value.data()

                        timestamp = get_datetime_64(
                            value_data[44:52]
                        )

                        record = OrderedDict([
                            ("plugin", u"AppCompat"),
                            ("name", value_name),
                            ("timestamp", timestamp),
                            ("path", location_path)
                        ])

                        print(u"{}".format(json.dumps(record, cls=ComplexEncoder)))
