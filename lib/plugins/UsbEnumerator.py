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

        hive = handler.get_hive()
        usbstore_path = u"\\".join([current_control_path, u"Enum\\USBSTOR"])
        usbstore_key = hive.find_key(usbstore_path)
        self._parse_usbstor(usbstore_key)

        usb_path = u"\\".join([current_control_path, u"Enum\\USB"])
        usb_key = hive.find_key(usb_path)
        self._parse_usb(usb_key)

    def _parse_usb(self, usb_key):
        for vid_pid_key in usb_key.subkeys():
            vid_pid_str = vid_pid_key.name()

            attributes = OrderedDict([])
            parts = vid_pid_str.split("&")
            for part in parts:
                attr_parts = part.split("_")
                attr_name = attr_parts[0]
                attr_value = attr_parts[1]

                attributes[attr_name.lower()] = attr_value

            record = OrderedDict([
                ("plugin", u"UsbEnumerator"),
            ])
            record["USB"] = attributes

            print(u"{}".format(json.dumps(record, cls=ComplexEncoder)))

    def _parse_usbstor(self, usbstore_key):
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
                last_arrival_date_str = None
                last_removal_date_str = None

                property_key = serial_number_key.subkey('Properties')
                if property_key:
                    key_1 = property_key.subkey('{83da6326-97a6-4088-9453-a1923f573b29}')
                    if key_1:
                        # InstallDate
                        install_date_key = key_1.subkey('0064')
                        if install_date_key is not None:
                            install_date_value = install_date_key.value()
                            if install_date_value is not None:
                                install_date_str = get_datetime_64(
                                    install_date_value.data()
                                )

                        # FirstInstallDate
                        first_install_date_key = key_1.subkey('0065')
                        if first_install_date_key is not None:
                            first_install_date_value = first_install_date_key.value()
                            if first_install_date_value is not None:
                                first_install_date_str = get_datetime_64(
                                    first_install_date_value.data()
                                )

                        # LastArrivalDate
                        last_arrival_key = key_1.subkey('0066')
                        if last_arrival_key is not None:
                            last_arrival_value = last_arrival_key.value()
                            if last_arrival_value is not None:
                                last_arrival_date_str = get_datetime_64(
                                    last_arrival_value.data()
                                )

                        # LastRemovalDate
                        last_removal_key = key_1.subkey('0067')
                        if last_removal_key is not None:
                            last_removal_value = last_removal_key.value()
                            if last_removal_value is not None:
                                last_removal_date_str = get_datetime_64(
                                    last_removal_value.data()
                                )

                record = OrderedDict([
                    ("plugin", u"UsbEnumerator"),
                    ("device_id", usbstore_device_name),
                    ("serial_number", serial_number_str),
                    ("friendly_name", friendly_name),
                    ("install_date", install_date_str),
                    ("first_install_date", first_install_date_str),
                    ("last_arrival_date", last_arrival_date_str),
                    ("last_removal_date", last_removal_date_str),
                ])

                print(u"{}".format(json.dumps(record, cls=ComplexEncoder)))

