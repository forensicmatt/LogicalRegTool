import json
import logging
from collections import OrderedDict
from lib.JsonDecoder import ComplexEncoder
from lib.Helpers import get_datetime_64
from lib.RegistryManager import enumerate_registry_value

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


def get_item_key_values(key_item):
    record = OrderedDict([])
    for value_item in key_item.values():
        value_name = value_item.name()
        value_data = value_item.data()

        value_data = enumerate_registry_value(
            value_data
        )
        record[value_name] = value_data

    return record


def get_device_properties(property_key):
    record = OrderedDict([])

    key_1 = property_key.subkey('{83da6326-97a6-4088-9453-a1923f573b29}')
    if key_1:
        # DriverNodeStrongName
        driver_node_key = key_1.subkey('0003')
        if driver_node_key is not None:
            driver_node_value = driver_node_key.value()
            if driver_node_value is not None:
                record['driver_node'] = enumerate_registry_value(
                    driver_node_value.data().decode('utf-16le')
                )

        # InstallDate
        install_date_key = key_1.subkey('0064')
        if install_date_key is not None:
            install_date_value = install_date_key.value()
            if install_date_value is not None:
                record['install_date'] = get_datetime_64(
                    install_date_value.data()
                )

        # FirstInstallDate
        first_install_date_key = key_1.subkey('0065')
        if first_install_date_key is not None:
            first_install_date_value = first_install_date_key.value()
            if first_install_date_value is not None:
                record['first_install_date'] = get_datetime_64(
                    first_install_date_value.data()
                )

        # LastArrivalDate
        last_arrival_key = key_1.subkey('0066')
        if last_arrival_key is not None:
            last_arrival_value = last_arrival_key.value()
            if last_arrival_value is not None:
                record['last_arrival_date'] = get_datetime_64(
                    last_arrival_value.data()
                )

        # LastRemovalDate
        last_removal_key = key_1.subkey('0067')
        if last_removal_key is not None:
            last_removal_value = last_removal_key.value()
            if last_removal_value is not None:
                record['last_removal_date'] = get_datetime_64(
                    last_removal_value.data()
                )

        #LastKnownParent
        last_known_parent_key = key_1.subkey('000A')
        if last_known_parent_key is not None:
            last_known_parent_value = last_known_parent_key.value()
            if last_known_parent_value is not None:
                record['last_known_parent'] = enumerate_registry_value(
                    last_known_parent_value.data().decode('utf-16le')
                )


    key_2 = property_key.subkey('{a8b865dd-2e3d-4094-ad97-e593a70c75d6}')
    if key_2:
        # DriverDate
        driver_date_key = key_2.subkey('0002')
        if driver_date_key is not None:
            driver_date_value = driver_date_key.value()
            if driver_date_value is not None:
                record['driver_date'] = get_datetime_64(
                    driver_date_value.data()
                )

        # DriverVersion
        driver_version_key = key_2.subkey('0003')
        if driver_version_key is not None:
            driver_version_value = driver_version_key.value()
            if driver_version_value is not None:
                record['driver_version'] = enumerate_registry_value(
                    driver_version_value.data().decode('utf-16le')
                )

        # DriverDescription
        driver_desc_key = key_2.subkey('0004')
        if driver_desc_key is not None:
            driver_desc_value = driver_desc_key.value()
            if driver_desc_value is not None:
                record['driver_description'] = enumerate_registry_value(
                    driver_desc_value.data().decode('utf-16le')
                )

        # Provider
        provider_key = key_2.subkey('0009')
        if provider_key is not None:
            provider_value = provider_key.value()
            if provider_value is not None:
                record['provider'] = enumerate_registry_value(
                    provider_value.data().decode('utf-16le')
                )

        # inf section
        inf_section_key = key_2.subkey('0006')
        if inf_section_key is not None:
            inf_section_value = inf_section_key.value()
            if inf_section_value is not None:
                record['inf_section'] = enumerate_registry_value(
                    inf_section_value.data().decode('utf-16le')
                )

        # matching device id
        matching_device_id_key = key_2.subkey('0008')
        if matching_device_id_key is not None:
            matching_device_id_value = matching_device_id_key.value()
            if matching_device_id_value is not None:
                record['matching_device_id'] = enumerate_registry_value(
                    matching_device_id_value.data().decode('utf-16le')
                )

        # driver rank
        driver_rank_key = key_2.subkey('000E')
        if driver_rank_key is not None:
            driver_rank_value = driver_rank_key.value()
            if driver_rank_value is not None:
                record['driver_rank'] = enumerate_registry_value(
                    driver_rank_value.data().decode('utf-16le')
                )

    key_3 = property_key.subkey('{540b947e-8b40-45bc-a8a2-6a0b894cbda2}')
    if key_3:
        # Configuration ID
        config_id_key = key_3.subkey('0007')
        if config_id_key is not None:
            config_id_value = config_id_key.value()
            if config_id_value is not None:
                record['configuration_id'] = enumerate_registry_value(
                    config_id_value.data().decode('utf-16le')
                )

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

        enum_base_path = u"\\".join([current_control_path, u"Enum"])
        enum_parser = EumParser(
            handler, enum_base_path
        )
        enum_parser.parse()

        enum_parser = EumParser(
            handler, "Setup\\Upgrade\\Pnp\\CurrentControlSet\\Control\\DeviceMigration\\Devices"
        )
        enum_parser.parse()

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


class EumParser(object):
    def __init__(self, system_handler, base_location):
        self.system_handler = system_handler
        self.base_location = base_location

    def parse(self):
        # Get the helper class for the SYSTEM handler
        system_helper = self.system_handler.get_helper()
        # Get the current control path
        current_control_path = system_helper.get_current_control_set_path()

        hive = self.system_handler.get_hive()

        scsi_path = u"\\".join([self.base_location, u"SCSI"])
        scsi_key = hive.find_key(scsi_path)
        self._parse_scsi(scsi_key)

        wpdbusenum_path = u"\\".join([self.base_location, u"SWD\\WPDBUSENUM"])
        wpdbusenum_key = hive.find_key(wpdbusenum_path)
        self._parse_wpdbusenum(wpdbusenum_key)

        usbstore_path = u"\\".join([self.base_location, u"USBSTOR"])
        usbstore_key = hive.find_key(usbstore_path)
        self._parse_usbstor(usbstore_key)

        usb_path = u"\\".join([self.base_location, u"USB"])
        usb_key = hive.find_key(usb_path)
        self._parse_usb(usb_key)

    def _parse_scsi(self, scsi_key):
        for device_item in scsi_key.subkeys():
            device_name = device_item.name()
            for serial_item in device_item.subkeys():
                record = OrderedDict([
                    ("_plugin", "UsbEnumerator.ENUM_SCSI"),
                    ("base_location", self.base_location)
                ])

                record['device'] = device_name
                record['serial'] = serial_item.name()

                item_values = get_item_key_values(
                    serial_item
                )
                record.update(item_values)

                property_key = serial_item.subkey('Properties')
                if property_key:
                    record['properties'] = get_device_properties(
                        property_key
                    )

                print(u"{}".format(json.dumps(record, cls=ComplexEncoder)))

    def _parse_wpdbusenum(self, wpdbusenum_key):
        for item_key in wpdbusenum_key.subkeys():
            item_name = item_key.name()

            record = OrderedDict([
                ("_plugin", "UsbEnumerator.ENUM_WPDBUSENUM"),
                ("base_location", self.base_location)
            ])

            # Attempt to parse key parts
            name_parts = get_parts_from_usb_string(
                item_name
            )

            record['name'] = item_name
            record['name_parts'] = name_parts

            item_values = get_item_key_values(
                item_key
            )
            record.update(item_values)

            property_key = item_key.subkey('Properties')
            if property_key:
                record['properties'] = get_device_properties(
                    property_key
                )

            print(u"{}".format(json.dumps(record, cls=ComplexEncoder)))

    def _parse_usbstor(self, usbstore_key):
        for device_subkey in usbstore_key.subkeys():
            usbstore_device_name = device_subkey.name()
            for serial_number_key in device_subkey.subkeys():
                record = OrderedDict([
                    ("_plugin", "UsbEnumerator.ENUM_USBSTOR"),
                    ("base_location", self.base_location)
                ])
                record['device'] = usbstore_device_name

                serial_number_str = serial_number_key.name()
                record['serial'] = serial_number_str

                item_values = get_item_key_values(
                    serial_number_key
                )
                record.update(item_values)

                property_key = serial_number_key.subkey('Properties')
                if property_key:
                    record['properties'] = get_device_properties(
                        property_key
                    )

                print(u"{}".format(json.dumps(record, cls=ComplexEncoder)))

    def _parse_usb(self, usb_key):
        for vid_pid_key in usb_key.subkeys():
            vid_pid_str = vid_pid_key.name()

            for serial_item in vid_pid_key.subkeys():
                serial_value = serial_item.name()
                record = OrderedDict([
                    ("_plugin", "UsbEnumerator.ENUM_USB"),
                    ("base_location", self.base_location)
                ])
                record['vid_pid'] = vid_pid_str
                record['serial'] = serial_value

                item_values = get_item_key_values(
                    serial_item
                )
                record.update(item_values)

                property_key = serial_item.subkey('Properties')
                if property_key:
                    record['properties'] = get_device_properties(
                        property_key
                    )

                print(u"{}".format(json.dumps(record, cls=ComplexEncoder)))
