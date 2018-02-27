import pytsk3
import logging
import argparse
from lib import RegistryManager as Rm
from lib import EnumHandlers as Eh
from lib.plugins.PluginManager import PluginManager

logging.basicConfig(
    level=logging.INFO
)


def get_arguments():
    usage = '''Process a logical volume.'''

    arguments = argparse.ArgumentParser(
        description=(usage)
    )
    arguments.add_argument(
        "-s", "--source",
        dest="source",
        action="store",
        required=True,
        type=unicode,
        help=u"Logical source [Example: \\\\.\\C:]"
    )

    return arguments


def main():
    arguments = get_arguments()
    options = arguments.parse_args()

    tsk_img = pytsk3.Img_Info(
        options.source
    )

    pm = PluginManager()

    reg_manager = Rm.RegistryManager()
    enumerator = Eh.LogicalEnumerator(
        tsk_img,
        reg_manager
    )
    enumerator.load_registry_files()

    pm.run_plugins(reg_manager)

    pass


if __name__ == "__main__":
    main()
