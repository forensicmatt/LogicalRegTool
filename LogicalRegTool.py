import pytsk3
import logging
import argparse
from lib import RegistryManager as Rm
from lib import EnumHandlers as Eh
from lib.plugins import PluginManager as Pm

VALID_DEBUG_LEVELS = ["ERROR", "WARN", "INFO", "DEBUG"]


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
        help="Logical source [Example: \\\\.\\C:]"
    )
    arguments.add_argument(
        "-t", "--temp_dir",
        dest="temp_dir",
        action="store",
        required=True,
        help="TEMP_DIR (Make sure this is on a volume that can handle large files.)"
    )
    arguments.add_argument(
        "-p", "--plugins",
        dest="plugins",
        action="store",
        default=None,
        help="Plugins to use (comma separated list) [{}]".format(",".join(Pm.ALL_PLUGINS))
    )
    arguments.add_argument(
        "--debug",
        dest="debug",
        action="store",
        default="ERROR",
        choices=VALID_DEBUG_LEVELS,
        help="Debug level [default=ERROR]"
    )

    return arguments


def set_debug_level(debug_level):
    if debug_level in VALID_DEBUG_LEVELS:
        logging.basicConfig(
            level=getattr(logging, debug_level)
        )
    else:
        raise(Exception("{} is not a valid debug level.".format(debug_level)))


def main():
    arguments = get_arguments()
    options = arguments.parse_args()

    set_debug_level(options.debug)

    tsk_img = pytsk3.Img_Info(
        options.source
    )

    plist = None
    if options.plugins:
        plist = Pm.plugin_list_from_string(options.plugins)

    pm = Pm.PluginManager(
        plugin_list=plist
    )

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
