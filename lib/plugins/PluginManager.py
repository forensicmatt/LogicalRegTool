from lib.plugins.RegistryIterator import RegistryIterator


class PluginManager(object):
    def __init__(self):
        self.plugins = [
            RegistryIterator()
        ]

    def run_plugins(self, registry_manager):
        for plugin in self.plugins:
            plugin.run(
                registry_manager
            )
