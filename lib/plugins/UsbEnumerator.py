import ujson
import json
import logging
from collections import OrderedDict
from lib.JsonDecoder import ComplexEncoder


class UsbEnumerator(object):
    def __init__(self):
        pass

    def run(self, registry_manager):
        handler = registry_manager.get_handler(u'SYSTEM')
        hive = handler.get_hive()

        key = hive.find_key(u'ControlSet001\\Enum\\USBSTOR')
        pass

