import ujson
import json
import logging
from collections import OrderedDict
from lib.JsonDecoder import ComplexEncoder


class RegistryIterator(object):
    def __init__(self):
        pass

    def run(self, registry_manager):
        for handler in registry_manager.iter_registry_handlers():
            logging.info(u"RegistryIterator -> {}".format(handler.registry_name))
            hive = handler.get_hive()
            root_key = hive.root_key()
            self.iter_key(root_key)

    def iter_key(self, key):
        name = key.name()
        full_path = u"\\".join([key.path(), name])
        logging.debug(u"Full Path: {}".format(full_path))

        key_timestamp = key.last_written_timestamp()

        try:
            for value in key.values():
                value_name = value.name()
                data_type_str = value.type_str()
                value_data = value.data()

                if isinstance(value_data, str):
                    value_data = value_data.decode(u'ascii', errors=u'replace')

                record = OrderedDict([
                    (u"full_path", u"\\".join([full_path, value_name])),
                    (u"value_name", value_name),
                    (u"data_type", data_type_str),
                    (u"value_data", value_data),
                    (u"last_written_timestamp", key_timestamp),
                    (u"deleted_flag", False)
                ])
                print(u"{}".format(json.dumps(record, cls=ComplexEncoder)))
        except Exception as error:
            logging.error(u"Error Type: {}; Path: {}; Error: {}".format(type(error), full_path, error))

        # Attempt to recover deleted keys
        for value in key.remnant_values():
            value_name = value.name()
            data_type_str = value.type_str()
            value_data = value.data()

            if isinstance(value_data, str):
                value_data = value_data.decode(u'ascii', errors=u'replace')

            record = OrderedDict([
                (u"full_path", u"\\".join([full_path, value_name])),
                (u"value_name", value_name),
                (u"data_type", data_type_str),
                (u"value_data", value_data),
                (u"last_written_timestamp", key_timestamp),
                (u"deleted_flag", True)
            ])
            print(u"{}".format(json.dumps(record, cls=ComplexEncoder)))

        for sub_key in key.subkeys():
            self.iter_key(sub_key)
