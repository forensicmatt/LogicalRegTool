import ujson
import json
import logging
from collections import OrderedDict
from lib.JsonDecoder import ComplexEncoder
from lib.Helpers import get_datetime_64


class UsbEnumerator(object):
    def __init__(self):
        pass

    def run(self, registry_manager):
        # Get the registry handler for the SYSTEM hive
        handler = registry_manager.get_handler(u'SYSTEM')

        # Get the helper class for the SYSTEM handler
        system_helper = handler.get_helper()

        # Get the current control path
        current_control_path = system_helper.get_current_control_set_path()
        usbstore_path = u"\\".join([current_control_path, u"Enum\\USBSTOR"])

        hive = handler.get_hive()
        usbstore_key = hive.find_key(usbstore_path)
        for device_subkey in usbstore_key.subkeys():
            usbstore_device_name = device_subkey.name()
            for serial_number_key in device_subkey.subkeys():
                serial_number_str = serial_number_key.name()

                # Friendly Name
                friendly_name_value = serial_number_key.value(name="FriendlyName")
                friendly_name = None
                if friendly_name_value:
                    friendly_name = friendly_name_value.data()
                    friendly_name = friendly_name.strip("\x00")

                # Other properties we can get
                install_date_str = None

                property_key = serial_number_key.subkey('Properties')
                if property_key:
                    key_1 = property_key.subkey('{83da6326-97a6-4088-9453-a1923f573b29}')
                    if key_1:
                        # InstallDate
                        install_date_key = key_1.subkey('0064')
                        if install_date_key:
                            install_date_value = install_date_key.value()
                            install_date_str = get_datetime_64(
                                install_date_value.data()
                            )

                        # FirstInstallDate
                        first_install_date_key = key_1.subkey('0065')
                        if first_install_date_key:
                            first_install_date_value = first_install_date_key.value()
                            first_install_date_str = get_datetime_64(
                                first_install_date_value.data()
                            )

                record = OrderedDict([
                    ("plugin", u"UsbEnumerator"),
                    ("device_id", usbstore_device_name),
                    ("serial_number", serial_number_str),
                    ("friendly_name", friendly_name),
                    ("install_date", install_date_str),
                    ("first_install_date", first_install_date_str),
                ])

                print(u"{}".format(json.dumps(record, cls=ComplexEncoder)))

