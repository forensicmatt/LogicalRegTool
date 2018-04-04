from lib.plugins.RegistryIterator import RegistryIterator
from lib.plugins.UsbEnumerator import UsbEnumerator
from lib.plugins.UserAssist import UserAssist
from lib.plugins.AppCompat import AppCompact
from lib.plugins.Bam import Bam

PLUGIN_MAPPING = {
    'UserAssist': UserAssist(),
    'AppCompact': AppCompact(),
    'Bam': Bam(),
    'UsbEnumerator': UsbEnumerator(),
    # 'RegistryIterator': RegistryIterator()
}

ALL_PLUGINS = [
    'UserAssist',
    'AppCompact',
    'Bam',
    'UsbEnumerator'
]


def plugin_list_from_string(plugin_str):
    plugin_list = plugin_str.split(',')

    for plugin in plugin_list:
        if plugin not in PLUGIN_MAPPING:
            raise(Exception("{} is not a valid plugin.".format(plugin)))

    return plugin_list


class PluginManager(object):
    def __init__(self, plugin_list=None):
        self.plugins = []

        if not plugin_list:
            plugin_list = ALL_PLUGINS

        for plugin in plugin_list:
            self.plugins.append(
                PLUGIN_MAPPING[plugin]
            )

    def run_plugins(self, registry_manager):
        for plugin in self.plugins:
            plugin.run(
                registry_manager
            )
