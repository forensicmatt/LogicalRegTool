import json
import logging
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
                    self.process_key_values_store(
                        location_path,
                        store_key
                    )

    def process_key_values_store(self, location_path, key):
        """Iterate values of the given key.
        """
        key_values = iter(key.values())
        remnant_values = iter(key.remnant_values())

        while True:
            try:
                value = next(key_values)
            except StopIteration:
                break
            except Exception as error:
                logging.error(u"Error getting next value: {}".format(error))
                continue

            value_name = value.name()
            value_data = value.data_raw()

            timestamp = get_datetime_64(
                value_data[44:52]
            )

            record = OrderedDict([
                ("_plugin", u"AppCompat"),
                ("name", value_name),
                ("timestamp", timestamp),
                ("path", location_path),
                ("deleted_flag", False)
            ])

            print(u"{}".format(json.dumps(record, cls=ComplexEncoder)))

        while True:
            try:
                value = next(remnant_values)
            except StopIteration:
                break
            except Exception as error:
                logging.error(u"Error getting next value: {}".format(error))
                continue

            value_name = value.name()
            value_data = value.data_raw()

            timestamp = None
            if len(value_data) > 52:
                timestamp = get_datetime_64(
                    value_data[44:52]
                )

            record = OrderedDict([
                ("_plugin", u"AppCompat"),
                ("name", value_name),
                ("timestamp", timestamp),
                ("path", location_path),
                ("deleted_flag", True)
            ])

            print(u"{}".format(json.dumps(record, cls=ComplexEncoder)))
