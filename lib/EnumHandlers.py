import re
import pytsk3
import logging
from lib.TskFileIo import TskFileIo
from lib.RegistryManager import RegistryHandler


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

    def load_registry_files(self):
        self._load_config_registry_files()

    def _load_config_registry_files(self):
        system_config_dir = self.fs_info.open_dir(u"./Windows/System32/config")
        dir_mapping = {}

        for tsk_file in system_config_dir:
            filename = tsk_file.info.name.name
            logging.debug(u"Filename: {}".format(filename))
            dir_mapping[filename] = {
                'fullname': u"/".join([u"./Windows/System32/config", filename]),
                'tsk_file': tsk_file,
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
