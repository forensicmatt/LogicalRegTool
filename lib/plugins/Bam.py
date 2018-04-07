import json
import logging
import traceback
from collections import OrderedDict
from lib.Helpers import get_datetime_64
from lib.JsonDecoder import ComplexEncoder


class Bam(object):
    _plugin_name = u"Bam"

    def __init__(self):
        pass

    def run(self, registry_manager):
        handler = registry_manager.get_handler(u'SYSTEM')
        system_helper = handler.get_helper()

        current_control_path = system_helper.get_current_control_set_path()
        bam_user_settings_path = u"\\".join([current_control_path, u"Services\\bam\\UserSettings"])

        hive = handler.get_hive()
        bam_user_settings_key = hive.find_key(bam_user_settings_path)
        if bam_user_settings_key:
            for sid_key in bam_user_settings_key.subkeys():
                sid_name = sid_key.name()

                version_value = sid_key.value(name=u"Version")
                version = None
                if version_value:
                    version = version_value.data()

                sequence_value = sid_key.value(name=u"SequenceNumber")
                sequence = None
                if sequence_value:
                    sequence = version_value.data()

                # We can have an issue with iterating values so we will take it one
                # at a time to try and catch errors.
                sid_key_values = iter(sid_key.values())

                while True:
                    try:
                        value = next(sid_key_values)
                    except StopIteration:
                        break
                    except Exception as error:
                        logging.error(u"Error getting next value: {}".format(error))
                        continue

                    value_name = value.name()
                    value_data = value.data_raw()

                    if value_name not in [u"Version", u"SequenceNumber"]:
                        timestamp = get_datetime_64(value_data[0:8])

                        record = OrderedDict([
                            ("_plugin", u"Bam"),
                            ("name", value_name),
                            ("timestamp", timestamp),
                            ("sid", sid_name),
                            ("version", version),
                            ("sequence", sequence)
                        ])

                        print(u"{}".format(json.dumps(record, cls=ComplexEncoder)))
        else:
            logging.info(u"[{}] {} not found.".format(self._plugin_name, bam_user_settings_path))
