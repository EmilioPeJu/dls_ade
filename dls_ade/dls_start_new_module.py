#!/bin/env dls-python
# This script comes from the dls_scripts python module
"""
Creates a new module and (unless otherwise indicated) imports it to the server.

Can currently create modules in the following areas:
- python
- tools
- support
- ioc (including BL gui)
"""

import sys
import json
import logging
from dls_ade.argument_parser import ArgParser
from dls_ade.get_module_creator import get_module_creator
from dls_ade import logconfig

usage = ("Default <area> is 'support'."
         "\nStart a new diamond module of a particular type."
         "\nUses makeBaseApp with the dls template for a 'support' or 'ioc' "
         "module, and uses default templates for both Python and Tools "
         "modules."
         "\nIf the --no-import flag is used, the module will not be exported "
         "to the server."
         "\nIf the -i flag is used, <module_name> is expected to be of the "
         "form 'Domain/Technical Area/IOC number' i.e. BL02I/VA/03"
         "\nThe IOC number can be omitted, in which case, it defaults to "
         '"01".'
         "\nIf the --fullname flag is used, the IOC will be imported as "
         "BL02I/BL02I-VA-IOC-03 (useful for multiple IOCs in the same "
         "technical area) and the IOC may optionally be specified as "
         "BL02I-VA-IOC-03 instead of BL02I/VA/03\nOtherwise it will be "
         "imported as BL02I/VA (old naming style)\nIf the Technical area is "
         "BL then a different template is used, to create a top level "
         "module for screens and gda.")


def make_parser():
    """
    Takes ArgParse instance with default arguments and adds

    Positional Arguments:
        * module_name

    Flags:
        * -n (no-import)
        * -f (fullname)

    Returns:
        :class:`argparse.ArgumentParser`:  ArgParse instance
    """
    supported_areas = ["support", "ioc", "python", "tools"]

    parser = ArgParser(usage, supported_areas)
    parser.add_module_name_arg()

    parser.add_argument(
        "-n", "--no-import", action="store_true", dest="no_import",
        help="Creates the module but doesn't store it on the server")
    parser.add_argument(
        "-f", "--fullname", action="store_true", dest="fullname",
        help="create new-style ioc, with full ioc name in path")

    return parser


def _main():
    log = logging.getLogger(name="dls_ade")
    usermsg = logging.getLogger("usermessages")

    parser = make_parser()
    args = parser.parse_args()

    log.info(json.dumps({'CLI': sys.argv, 'options_args': vars(args)}))

    module_name = args.module_name
    area = args.area
    fullname = args.fullname
    export_to_server = not args.no_import

    module_creator = get_module_creator(module_name, area, fullname)

    module_creator.verify_can_create_local_module()

    if export_to_server:
        module_creator.verify_remote_repo()

    module_creator.create_local_module()

    if export_to_server:
        module_creator.push_repo_to_remote()

    msg = module_creator.get_print_message()
    usermsg.info(msg)


def main():
    # Catch unhandled exceptions and ensure they're logged
    try:
        logconfig.setup_logging(application='dls-start-new-module.py')
        return _main()
    except Exception as e:
        logging.exception(e)
        logging.getLogger("usermessages").exception("ABORT: Unhandled exception (see trace below): {}".format(e))
        exit(1)


if __name__ == "__main__":
    sys.exit(main())
