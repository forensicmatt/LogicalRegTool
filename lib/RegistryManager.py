import re
import logging
from yarp import Registry


class RegistryHandler(object):
    def __init__(self, registry_name, fullname, tsk_file_io):
        self.registry_name = registry_name
        self.fullname = fullname
        self.tsk_file_io = tsk_file_io
        self.log_files = {
            1: None,
            2: None,
            3: None
        }

    def enumerate_log_files(self, mapping):
        file_list = mapping.keys()
        for key in sorted(file_list):
            match = re.search('^{}[.]LOG(\d)$'.format(self.registry_name), key, flags=re.I)
            if match:
                number = int(match.group(1))
                self.log_files[number] = mapping[key]

    def get_hive(self):
        hive = Registry.RegistryHive(self.tsk_file_io)
        try:
            recovery_result = hive.recover_auto(
                getattr(self.log_files[1], 'tsk_file', None),
                getattr(self.log_files[2], 'tsk_file', None),
                getattr(self.log_files[3], 'tsk_file', None)
            )
            logging.info(u"Recovery Results: {}".format(recovery_result))
        except Exception as error:
            logging.error(u"{}".format(error))

        return hive


class RegistryManager(object):
    def __init__(self):
        self.mapping = []

    def add_registry(self, handler):
        self.mapping.append(
            handler
        )

    def iter_registry_handlers(self):
        for handler in self.mapping:
            yield handler
