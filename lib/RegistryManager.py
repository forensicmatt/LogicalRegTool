import re
import os
import sys
import logging
from yarp import Registry
from yarp import RegistrySqlite
from lib.Helpers import extract_tsk_file_temp


class SystemHelper(object):
    def __init__(self, handler):
        self._handler = handler

    def get_current_control_set_path(self):
        hive = self._handler.get_hive()
        select_key = hive.find_key(u'Select')
        if select_key:
            current_value = select_key.value(name=u"Current")
            current_path = u"ControlSet{:03d}".format(current_value.data())
            return current_path
        else:
            raise Exception(u"Cannot find 'Select' key in SOFTWARE hive.")


class RegistryHandler(object):
    def __init__(self, registry_name, name_key, mapping, temp_dir):
        self.registry_name = registry_name
        self.orig_name = name_key
        self.orig_filename = mapping[name_key]['fullname']
        self.temp_dir = temp_dir
        self.sqlite_hive = os.path.join(self.temp_dir, u"{}.db".format(self.registry_name))
        self.primary_registry = os.path.join(self.temp_dir, name_key)

        self.log_files = {
            u'LOG': None,
            u'LOG1': None,
            u'LOG2': None
        }

        logging.debug(u"[starting] Processing: {} and logfiles.".format(self.orig_filename))

        # Insure temp dir
        if not os.path.isdir(self.temp_dir):
            os.makedirs(self.temp_dir)

        # extract main hive
        export_file_io = open(self.primary_registry, 'wb')
        extract_tsk_file_temp(mapping[name_key], export_file_io)

        file_list = mapping.keys()
        for key in sorted(file_list):
            match = re.search('^{}[.](LOG\d?)$'.format(self.registry_name), key, flags=re.I)
            if match:
                filename = match.group(0)

                if mapping[key]['attribute'].id is None:
                    continue

                export_fullpath = os.path.join(self.temp_dir, filename)
                export_file_io = open(export_fullpath, 'wb')

                # Extract the source file to the temp file
                extract_tsk_file_temp(
                    mapping[key], export_file_io
                )

                log = match.group(1)
                self.log_files[log] = export_fullpath

        # We are not currently using YarpDB, will do SQLite init once utilized
        # if sys.version_info > (3, 0):
        #     hive = RegistrySqlite.YarpDB(
        #         self.primary_registry,
        #         self.sqlite_hive
        #     )
        #     hive.close()

        logging.debug(u"[finished] Processing: {}".format(self.orig_filename))

    def get_sqlite_hive(self):
        """Get the YarpDB class of a hive.
        """
        # Not currently used

        # hive = RegistrySqlite.YarpDB(
        #     None,
        #     self.sqlite_hive
        # )
        # return hive
        pass

    def get_hive(self):
        """Get the RegistryHive for this handler.
        """
        hive = Registry.RegistryHive(
            open(self.primary_registry, 'rb')
        )

        try:
            if self.log_files[u'LOG']:
                log_1 = open(self.log_files[u'LOG'], 'rb')
            else:
                log_1 = None

            if self.log_files[u'LOG1']:
                log_2 = open(self.log_files[u'LOG1'], 'rb')
            else:
                log_2 = None

            if self.log_files[u'LOG2']:
                log_3 = open(self.log_files[u'LOG2'], 'rb')
            else:
                log_3 = None

            recovery_result = hive.recover_auto(
                log_1,
                log_2,
                log_3
            )
            logging.info(u"Recovery Results: {}".format(recovery_result))
        except Exception as error:
            logging.error(u"{}".format(error))

        return hive

    def get_helper(self):
        if self.registry_name.upper() == u"SYSTEM":
            return SystemHelper(self)
        else:
            raise Exception(u"No Helper for registry {}".format(self.registry_name))

    def __del__(self):
        logging.debug(u"RegistryHandler.__del__")
        # os.rmdir(self.temp_dir)


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
