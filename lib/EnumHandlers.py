import re
import os
import pytsk3
import logging
from lib.TskFileIo import TskFileIo
from lib.RegistryManager import RegistryHandler

# User class location dir ./[USERS_FOLDER]/[USER]/AppData/Local/Microsoft/Windows
USRCLASS_DIR_TEMPLATE = u"./{}/{}/AppData/Local/Microsoft/Windows"
# NTUSER location dir ./[USERS_FOLDER]/[USER]
NTUSER_DIR_TEMPLATE = u"./{}/{}"


def get_temp_dir(temp_base, registry, inode, user=None):
    temp_dir = u"{}.{}".format(registry, inode)

    if user:
        temp_dir = u"{}_{}".format(user, temp_dir)

    temp_dir = os.path.join(temp_base, temp_dir)
    return temp_dir


class ExtractionAttribute(object):
    def __init__(self, tsk_file, fullname=None):
        """Sometimes a file might not have a data attribute. This way we know if a file has a data attribute accessible.
        """
        self.id = None
        self.type = None
        self.size = None
        self.attribute_name = None

        ntfs_attr_found = False

        for attr in tsk_file:
            if attr.info.type == pytsk3.TSK_FS_ATTR_TYPE_NTFS_DATA:
                ntfs_attr_found = True
                self.id = attr.info.id
                self.type = attr.info.type
                self.size = attr.info.size
                self.attribute_name = attr.info.name
                break

        if not ntfs_attr_found:
            name = tsk_file.info.name.name
            if fullname:
                name = fullname
            logging.warn(u"No TSK_FS_ATTR_TYPE_NTFS_DATA attribute found for {}".format(name))


class LogicalEnumerator(object):
    """A class to process the logical volume."""
    def __init__(self, temp_dir, img_info, registry_manager):
        """Create LogicalEnumerator

        Params:
            temp_dir (unicode): the location of the temp dir.
            img_info (FileIO): a file like object representing a volume.
            registry_manager (RegistryManager): class managing operations for multiple registries
        """
        self.temp_dir = temp_dir
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
                        filename = tsk_file.info.name.name.decode(u"utf-8")
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
                    filename = tsk_file.info.name.name.decode(u"utf-8")
                    logging.debug(u"Filename: {}".format(filename))
                    fullname = u"/".join([ntuser_path, filename])

                    dir_mapping[filename] = {
                        'fullname': u"/".join([ntuser_path, fullname]),
                        'tsk_file': tsk_file,
                        'attribute': ExtractionAttribute(
                            tsk_file, fullname=fullname
                        )
                    }

                for key in dir_mapping.keys():
                    tsk_file = dir_mapping[key]['tsk_file']
                    inode = None
                    if tsk_file.info.meta:
                        inode = tsk_file.info.meta.addr
                    else:
                        continue

                    if re.search('^NTUSER.DAT$', key, flags=re.I):
                        temp_dir = get_temp_dir(
                            self.temp_dir, u'NTUSER.DAT', inode,
                            user=user_name
                        )

                        handler = RegistryHandler(
                            u'NTUSER.DAT',
                            key,
                            dir_mapping,
                            temp_dir
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
                    filename = tsk_file.info.name.name.decode(u"utf-8")
                    logging.debug(u"Filename: {}".format(filename))
                    fullname = u"/".join([usrclass_path, filename])

                    dir_mapping[filename] = {
                        'fullname': fullname,
                        'tsk_file': tsk_file,
                        'attribute': ExtractionAttribute(
                            tsk_file, fullname=fullname
                        )
                    }

                for key in dir_mapping.keys():
                    tsk_file = dir_mapping[key]['tsk_file']
                    inode = None
                    if tsk_file.info.meta:
                        inode = tsk_file.info.meta.addr
                    else:
                        continue

                    if re.search('^UsrClass.Dat$', key, flags=re.I):
                        temp_dir = get_temp_dir(
                            self.temp_dir, u'UsrClass.Dat', inode,
                            user=user_name
                        )

                        handler = RegistryHandler(
                            u'UsrClass.Dat',
                            key,
                            dir_mapping,
                            temp_dir
                        )
                        self.registry_manager.add_registry(
                            handler
                        )

    def _load_config_registry_files(self):
        system_config_dir = self.fs_info.open_dir(u"./Windows/System32/config")
        dir_mapping = {}

        for tsk_file in system_config_dir:
            filename = tsk_file.info.name.name.decode(u"utf-8")
            logging.debug(u"Filename: {}".format(filename))
            fullname = u"/".join([u"./Windows/System32/config", filename])

            dir_mapping[filename] = {
                'fullname': fullname,
                'tsk_file': tsk_file,
                'attribute': ExtractionAttribute(
                    tsk_file, fullname=fullname
                )
            }

        for key in dir_mapping.keys():
            tsk_file = dir_mapping[key]['tsk_file']
            inode = None
            if tsk_file.info.meta:
                inode = tsk_file.info.meta.addr
            else:
                continue

            if re.search('^SYSTEM$', key, flags=re.I):
                temp_dir = get_temp_dir(
                    self.temp_dir, u'SYSTEM', inode
                )

                handler = RegistryHandler(
                    u'SYSTEM',
                    key,
                    dir_mapping,
                    temp_dir
                )
                self.registry_manager.add_registry(
                    handler
                )
            elif re.search('^SOFTWARE$', key, flags=re.I):
                temp_dir = get_temp_dir(
                    self.temp_dir, u'SOFTWARE', inode
                )

                handler = RegistryHandler(
                    u'SOFTWARE',
                    key,
                    dir_mapping,
                    temp_dir
                )
                self.registry_manager.add_registry(
                    handler
                )
            elif re.search('^SECURITY$', key, flags=re.I):
                temp_dir = get_temp_dir(
                    self.temp_dir, u'SECURITY', inode
                )

                handler = RegistryHandler(
                    u'SECURITY',
                    key,
                    dir_mapping,
                    temp_dir
                )
                self.registry_manager.add_registry(
                    handler
                )
            elif re.search('^SAM$', key, flags=re.I):
                temp_dir = get_temp_dir(
                    self.temp_dir, u'SAM', inode
                )

                handler = RegistryHandler(
                    u'SAM',
                    key,
                    dir_mapping,
                    temp_dir
                )
                self.registry_manager.add_registry(
                    handler
                )

    def __del__(self):
        logging.debug(u"LogicalEnumerator.__del__")

