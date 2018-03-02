import re
import pytsk3
import logging
from lib.TskFileIo import TskFileIo
from lib.RegistryManager import RegistryHandler

# User class location dir ./[USERS_FOLDER]/[USER]/AppData/Local/Microsoft/Windows
USRCLASS_DIR_TEMPLATE = u"./{}/{}/AppData/Local/Microsoft/Windows"
# NTUSER location dir ./[USERS_FOLDER]/[USER]
NTUSER_DIR_TEMPLATE = u"./{}/{}"


class LogicalEnumerator(object):
    """A class to process the logical volume."""
    def __init__(self, img_info, registry_manager):
        """Create LogicalEnumerator

        Params:
            file_io (FileIO): I file like object representing a volume.
            handler_mapping (ArtifactMapping): The artifact mapping that determines file operations
            arango_handler (ArangoHandler): The handler for inserting documents into ArangoDB
            temp_dir (unicode): The location to extract files to
            description (unicode): The label for this LogicalEnumerator
        """
        self.img_info = img_info
        self.fs_info = pytsk3.FS_Info(
            self.img_info
        )
        self.registry_manager = registry_manager

        # This will contain the location of the users folder if available
        self._users_folder_location = None
        self._users_folder_folders = []

    def load_registry_files(self):
        self._load_config_registry_files()
        self._load_user_registry_files()

    def _enum_user_folders(self):
        """Try to enumerate the user folders.
        """
        try:
            user_folder = self.fs_info.open_dir(u"./Users")
            self._users_folder_location = u"Users"
        except Exception:
            logging.info(u"No users dir at ./Users")

        if not user_folder:
            try:
                user_folder = self.fs_info.open_dir(u"./Documents and Settings")
                self._users_folder_location = u"Documents and Settings"
            except Exception:
                logging.info(u"No users dir at ./Documents and Settings")

        if user_folder:
            for tsk_file in user_folder:
                # Check if this folder is a dir
                if tsk_file.info.meta is not None:
                    if tsk_file.info.meta.type == pytsk3.TSK_FS_META_TYPE_DIR:
                        filename = unicode(tsk_file.info.name.name)
                        if filename in [u'.', u'..']:
                            continue

                        self._users_folder_folders.append(
                            filename
                        )

    def _load_user_registry_files(self):
        self._enum_user_folders()
        if self._users_folder_location is not None:
            for user_name in self._users_folder_folders:
                # Get NTUSERs
                ntuser_path = NTUSER_DIR_TEMPLATE.format(self._users_folder_location, user_name)
                ntuser_dir = self.fs_info.open_dir(ntuser_path)
                dir_mapping = {}

                for tsk_file in ntuser_dir:
                    filename = tsk_file.info.name.name
                    logging.debug(u"Filename: {}".format(filename))
                    dir_mapping[filename] = {
                        'fullname': u"/".join([ntuser_path, filename]),
                        'tsk_file': tsk_file,
                        'file_io': TskFileIo(tsk_file)
                    }

                for key in dir_mapping.keys():
                    if re.search('^NTUSER.DAT$', key, flags=re.I):
                        handler = RegistryHandler(
                            u'NTUSER.DAT',
                            dir_mapping[key]['fullname'],
                            TskFileIo(dir_mapping[key]['tsk_file'])
                        )
                        handler.enumerate_log_files(
                            dir_mapping
                        )
                        self.registry_manager.add_registry(
                            handler
                        )

                usrclass_path = USRCLASS_DIR_TEMPLATE.format(self._users_folder_location, user_name)
                try:
                    usrclass_dir = self.fs_info.open_dir(usrclass_path)
                except Exception as error:
                    logging.info(u"{}".format(error))
                    continue

                dir_mapping = {}

                for tsk_file in usrclass_dir:
                    filename = tsk_file.info.name.name
                    logging.debug(u"Filename: {}".format(filename))
                    dir_mapping[filename] = {
                        'fullname': u"/".join([usrclass_path, filename]),
                        'tsk_file': tsk_file,
                        'file_io': TskFileIo(tsk_file)
                    }

                for key in dir_mapping.keys():
                    if re.search('^UsrClass.Dat$', key, flags=re.I):
                        handler = RegistryHandler(
                            u'UsrClass.Dat',
                            dir_mapping[key]['fullname'],
                            TskFileIo(dir_mapping[key]['tsk_file'])
                        )
                        handler.enumerate_log_files(
                            dir_mapping
                        )
                        self.registry_manager.add_registry(
                            handler
                        )

    def _load_config_registry_files(self):
        system_config_dir = self.fs_info.open_dir(u"./Windows/System32/config")
        dir_mapping = {}

        for tsk_file in system_config_dir:
            filename = tsk_file.info.name.name
            logging.debug(u"Filename: {}".format(filename))
            dir_mapping[filename] = {
                'fullname': u"/".join([u"./Windows/System32/config", filename]),
                'tsk_file': tsk_file,
                'file_io': TskFileIo(tsk_file)
            }

        for key in dir_mapping.keys():
            if re.search('^SYSTEM$', key, flags=re.I):
                handler = RegistryHandler(
                    u'SYSTEM',
                    dir_mapping[key]['fullname'],
                    TskFileIo(dir_mapping[key]['tsk_file'])
                )
                handler.enumerate_log_files(
                    dir_mapping
                )
                self.registry_manager.add_registry(
                    handler
                )
            elif re.search('^SOFTWARE$', key, flags=re.I):
                handler = RegistryHandler(
                    u'SOFTWARE',
                    dir_mapping[key]['fullname'],
                    TskFileIo(dir_mapping[key]['tsk_file'])
                )
                handler.enumerate_log_files(
                    dir_mapping
                )
                self.registry_manager.add_registry(
                    handler
                )
            elif re.search('^SECURITY$', key, flags=re.I):
                handler = RegistryHandler(
                    u'SECURITY',
                    dir_mapping[key]['fullname'],
                    TskFileIo(dir_mapping[key]['tsk_file'])
                )
                handler.enumerate_log_files(
                    dir_mapping
                )
                self.registry_manager.add_registry(
                    handler
                )
            elif re.search('^SAM$', key, flags=re.I):
                handler = RegistryHandler(
                    u'SAM',
                    dir_mapping[key]['fullname'],
                    TskFileIo(dir_mapping[key]['tsk_file'])
                )
                handler.enumerate_log_files(
                    dir_mapping
                )
                self.registry_manager.add_registry(
                    handler
                )
