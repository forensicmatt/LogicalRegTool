import pytsk3
import logging
import argparse
from lib import RegistryManager as Rm
from lib import EnumHandlers as Eh
from lib.plugins.PluginManager import PluginManager

logging.basicConfig(
    level=logging.DEBUG
)


def get_arguments():
    usage = '''Process registry files from a logical volume. The output is in JSONL format. 
    This tool requires Admin privlages to open the Logical Volume.'''

    arguments = argparse.ArgumentParser(
        description=(usage)
    )
    arguments.add_argument(
        "-s", "--source",
        dest="source",
        action="store",
        required=True,
        help=u"Logical source [Example: \\\\.\\C:]"
    )
    arguments.add_argument(
        "-t", "--temp_dir",
        dest="temp_dir",
        action="store",
        required=True,
        help=u"TEMP_DIR (Make sure this is on a volume that can handle large files.)"
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
        options.temp_dir,
        tsk_img,
        reg_manager
    )
    enumerator.load_registry_files()

    pm.run_plugins(reg_manager)


if __name__ == "__main__":
    main()
