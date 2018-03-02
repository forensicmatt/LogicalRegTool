import re
import logging
from yarp import Registry


class RegistryHandler(object):
    def __init__(self, registry_name, fullname, tsk_file_io):
        self.registry_name = registry_name
        self.fullname = fullname
        self.tsk_file_io = tsk_file_io
        self.log_files = {
            u'1': {},
            u'2': {},
            u'3': {}
        }

    def enumerate_log_files(self, mapping):
        file_list = mapping.keys()
        for key in sorted(file_list):
            match = re.search('^{}[.]LOG(\d)$'.format(self.registry_name), key, flags=re.I)
            if match:
                number = unicode(match.group(1))
                self.log_files[number] = mapping[key]

    def get_hive_new(self):
        hive = Registry.RegistryHive(self.tsk_file_io)

        log_1 = self.log_files[u'1'].get(u'file_io', None)
        if log_1:
            log_2 = self.log_files[u'2'].get(u'file_io', None)
            hive.recover_new(
                log_1 , file_object_log2=log_2
            )
            return hive

        return None

    def get_hive(self):
        hive = Registry.RegistryHive(self.tsk_file_io)
        try:
            log_1 = self.log_files[u'1'].get(u'file_io', None)
            log_2 = self.log_files[u'2'].get(u'file_io', None)
            log_3 = self.log_files[u'3'].get(u'file_io', None)
            recovery_result = hive.recover_auto(
                None,
                log_1,
                log_2
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

    def iter_registry_handlers(self, name=None):
        for handler in self.mapping:
            if name:
                if name.lower() == handler.registry_name.lower():
                    yield handler
            else:
                yield handler

    def get_handler(self, name):
        for handler in self.mapping:
            if handler.registry_name.lower() == name.lower():
                return handler

    def get_windows_version(self):
        software_handler = self.get_handler(name=u'SOFTWARE')
        if software_handler is not None:
            hive = software_handler.get_hive()
            current_version_key = hive.find_key(u'Microsoft\\Windows NT\\CurrentVersion')
            if current_version_key is not None:
                current_version_value = current_version_key.value(name=u'CurrentVersion')
                current_major_version_value = current_version_key.value(name=u'CurrentMajorVersionNumber')
                product_name_value = current_version_key.value(name=u'ProductName')
                product_name_string = product_name_value.data()

                version_number = None
                if current_major_version_value is not None:
                    version_number = current_major_version_value.data()
                elif current_version_value is not None:
                    version_number = current_version_value.data()

                return product_name_string, version_number

        return None, None
