import json
import codecs
import struct
from collections import OrderedDict
from lib.JsonDecoder import ComplexEncoder


class UserAssist(object):
    def __init__(self):
        pass

    def run(self, registry_manager):
        for reg_handler in registry_manager.iter_registry_handlers(name=u'NTUSER.DAT'):
            hive = reg_handler.get_hive()

            user_assist_key = hive.find_key(u'Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\UserAssist')
            if user_assist_key is not None:
                for guid_key in user_assist_key.subkeys():
                    guid_key_name = guid_key.name()

                    count_key = guid_key.subkey(u"Count")
                    if count_key is not None:
                        for value in count_key.values():
                            value_name = value.name()
                            value_name_decoded = codecs.encode(value_name, 'rot_13')
                            value_data = value.data()

                            count = None
                            if len(value_data) == 16:
                                count = struct.unpack("<I",value_data[4:8])[0]
                                count -= 5
                            elif len(value_data) == 72:
                                count = struct.unpack("<I", value_data[4:8])[0]

                            record = OrderedDict([
                                ("plugin", u"UserAssist"),
                                ("guid", guid_key_name),
                                ("name", value_name_decoded),
                                ("count", count)
                            ])

                            print(u"{}".format(json.dumps(record, cls=ComplexEncoder)))
