from lib.plugins.RegistryIterator import RegistryIterator
from lib.plugins.UsbEnumerator import UsbEnumerator
from lib.plugins.UserAssist import UserAssist
from lib.plugins.AppCompat import AppCompact
from lib.plugins.Bam import Bam


class PluginManager(object):
    def __init__(self):
        self.plugins = [
            # RegistryIterator(),
            UserAssist(),
            AppCompact(),
            Bam(),
            UsbEnumerator()
        ]

    def run_plugins(self, registry_manager):
        for plugin in self.plugins:
            plugin.run(
                registry_manager
            )
