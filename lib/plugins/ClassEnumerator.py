import json
import collections
from lib.JsonDecoder import ComplexEncoder


class ClassEnumerator(object):
    def __init__(self):
        pass

    def run(self, registry_manager):
        handler = registry_manager.get_handler(u'SYSTEM')
        system_helper = handler.get_helper()

        mapping = system_helper.get_class_mapping()

        for key, value in mapping.items():
            record = collections.OrderedDict([
                ("_plugin", "ClassEnumerator")
            ])
            record['guid'] = key
            record.update(value)
            print(u"{}".format(json.dumps(record, cls=ComplexEncoder)))
