import json
import logging
from collections import OrderedDict
from lib.JsonDecoder import ComplexEncoder
from lib.Helpers import get_datetime_64


# Resources:
# https://www.magnetforensics.com/computer-forensics/how-to-analyze-usb-device-history-in-windows/


def get_parts_from_usb_string(usb_str):
    # Examples:
    # _??_USBSTOR#Disk&Ven_Flash&Prod_Drive_SM_USB20&Rev_1100#AA04012700013494&0#{53f56307-b6bf-11d0-94f2-00a0c91efb8b}
    # {8dfc9df3-376f-11e3-be88-24fd52566ede}#0000000000100000

    # Attempt to parse key parts
    record = OrderedDict([])
    record["raw"] = usb_str

    parts = usb_str.split("#")
    if len(parts) == 4:
        record["type"] = parts[0]
        record["desc"] = parts[1]
        record["serial"] = parts[2]
        record["guid"] = parts[3]
    elif len(parts) == 2:
        record["guid"] = parts[0]
        record["serial"] = parts[1]
    else:
        logging.info("get_parts_from_usb_string() - Unknown parts parsing: {}".format(usb_str))

    return record


class UsbEnumerator(object):
    def __init__(self):
        pass

    def run(self, registry_manager):
        # Get the registry handler for the SYSTEM hive
        handler = registry_manager.get_handler(u'SYSTEM')
        self._handle_system_hive(handler)

    def _handle_system_hive(self, handler):
        # Get the helper class for the SYSTEM handler
        system_helper = handler.get_helper()
        # Get the current control path
        current_control_path = system_helper.get_current_control_set_path()

        hive = handler.get_hive()
        mounted_devices_path = u"MountedDevices"
        mounted_devices_key = hive.find_key(mounted_devices_path)
        self._mounted_devices(mounted_devices_key)

        device_migration_path = u"\\".join([current_control_path, u"Control\\DeviceMigration\\Classes\\{4d36e967-e325-11ce-bfc1-08002be10318}"])
        device_migration_key = hive.find_key(device_migration_path)
        self._device_migration(device_migration_key)

        wpdbusenum_path = u"\\".join([current_control_path, u"Enum\\SWD\\WPDBUSENUM"])
        wpdbusenum_key = hive.find_key(wpdbusenum_path)
        self._parse_wpdbusenum(wpdbusenum_key)

        usbstore_path = u"\\".join([current_control_path, u"Enum\\USBSTOR"])
        usbstore_key = hive.find_key(usbstore_path)
        self._parse_usbstor(usbstore_key)

        usb_path = u"\\".join([current_control_path, u"Enum\\USB"])
        usb_key = hive.find_key(usb_path)
        self._parse_usb(usb_key)

    def _device_migration(self, device_migration_key):
        for item in device_migration_key.values():
            value_name = item.name()

            device_parts = value_name.split("\\")
            device = OrderedDict([
                ("name", value_name)
            ])

            if len(device_parts) == 3:
                device['type'] = device_parts[0]
                device['desc'] = device_parts[1]
                device['serial'] = device_parts[2]

            record = OrderedDict([
                ("_plugin", "UsbEnumerator.DeviceMigration"),
                ("guid", "{4d36e967-e325-11ce-bfc1-08002be10318}"),
                ("device", device)
            ])

            print(u"{}".format(json.dumps(record, cls=ComplexEncoder)))

    def _mounted_devices(self, mounted_devices_key):
        for item in mounted_devices_key.values():
            record = OrderedDict([
                ("_plugin", "UsbEnumerator.MountedDevices")
            ])

            value_name = item.name()
            value_data = item.data()

            record["mount"] = value_name

            if value_data.startswith(b"_\x00?\x00?\x00") or value_data.startswith(b"\\\x00?\x00?\x00"):
                value_data = get_parts_from_usb_string(value_data.decode('utf-16le'))
                record["device"] = value_data
            else:
                value_data = value_data.hex()
                record["raw"] = value_data

            print(u"{}".format(json.dumps(record, cls=ComplexEncoder)))

    def _parse_wpdbusenum(self, wpdbusenum_key):
        for item_key in wpdbusenum_key.subkeys():
            item_name = item_key.name()

            record = OrderedDict([
                ("_plugin", "UsbEnumerator.WPDBUSENUM")
            ])

            # Attempt to parse key parts
            name_parts = get_parts_from_usb_string(item_name)

            record['name'] = item_name
            record['name_parts'] = name_parts
            record['capabilities'] = item_key.value(name='Capabilities').data()
            record['container_id'] = item_key.value(name='ContainerID').data().strip("\x00")
            cids = []
            for cid in item_key.value(name='CompatibleIDs').data():
                cids.append(cid.strip("\x00"))
            record['container_ids'] = cids
            record['config_flags'] = item_key.value(name='ConfigFlags').data()
            record['class_guid'] = item_key.value(name='ClassGUID').data().strip("\x00")
            record['driver'] = item_key.value(name='Driver').data().strip("\x00")
            record['mfg'] = item_key.value(name='Mfg').data().strip("\x00")
            record['service'] = item_key.value(name='Service').data().strip("\x00")
            record['device_desc'] = item_key.value(name='DeviceDesc').data().strip("\x00")
            record['friendly_name'] = item_key.value(name='FriendlyName').data().strip("\x00")

            print(u"{}".format(json.dumps(record, cls=ComplexEncoder)))

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
                ("_plugin", "UsbEnumerator.USB")
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
                    ("_plugin", "UsbEnumerator.USBSTOR"),
                    ("device_id", usbstore_device_name),
                    ("serial_number", serial_number_str),
                    ("friendly_name", friendly_name),
                    ("install_date", install_date_str),
                    ("first_install_date", first_install_date_str),
                    ("last_arrival_date", last_arrival_date_str),
                    ("last_removal_date", last_removal_date_str),
                ])

                print(u"{}".format(json.dumps(record, cls=ComplexEncoder)))

