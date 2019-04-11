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
import argparse
from dls_ade.argument_parser import ArgParser
from dls_ade.get_module_creator import get_module_creator
from dls_ade import logconfig, Server
from dls_ade.dls_utilities import remove_git_at_end
from dls_ade.exceptions import VerificationError, ParsingError

usage = ("""Default <area> is 'support'.
Start a new Diamond module of a particular type, using a template appropriate 
for the chosen area. In the case of 'support' or 'ioc' modules, makeBaseApp is 
used with the DLS template.

The module is created locally in the current working directory. Unless the 
--no-import flag is used, a remote repository will then be created on the server
and an initial commit pushed to it.

IOC modules:
    If the --ioc flag is used, <module_name> is expected to be of the 
    form '<Domain>/<Domain>-<Technical area>-IOC-<Number>' 
    i.e. BL02I/BL02I-VA-IOC-03 

Beamline UI modules:
    If the Technical Area is UI then a special template is used, 
    to create a top level module for screens and gda,
    e.g. BL02I/BL02I-UI-IOC-01""")


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
    parser.formatter_class=argparse.RawDescriptionHelpFormatter

    parser.add_argument(
        "-f", "--fullname", action="store_true", dest="fullname",
        help="Create new-style ioc, with full ioc name in path"
    )

    # The following arguments cannot be used together
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-n", "--no-import", action="store_true", dest="no_import",
        help="Creates the module but doesn't store it on the server"
    )

    group.add_argument(
        "-e", "--empty", action="store_true", dest="empty",
        help="Initialize an empty remote repository on the server. Does not "
             "create a local repo nor commit any files."
    )

    parser.add_argument(
        "-q", "--ignore_existing", action="store_true", dest="ignore_existing",
        help="When used together with -e/--empty, this script will exit "
             "silently with success if a repository with the given name "
             "already exists on the server."
    )

    return parser


def verify_args(args):
    if args.ignore_existing and not args.empty:
        raise VerificationError(
            "--ignore_existing can only be used with --empty"
        )


def _main():
    log = logging.getLogger(name="dls_ade")
    usermsg = logging.getLogger("usermessages")

    parser = make_parser()
    args = parser.parse_args()

    try:
        verify_args(args)
    except VerificationError as e:
        usermsg.error(e.message)
        return 1

    log.info(json.dumps({'CLI': sys.argv, 'options_args': vars(args)}))

    module_name = args.module_name
    area = args.area
    fullname = args.fullname
    create_empty_remote_only = args.empty
    export_to_server = not args.no_import

    if create_empty_remote_only:
        try:
            create_empty_remote(area, module_name)
            usermsg.info(
                "Created new empty remote repo %s/%s", area, module_name
            )
        except VerificationError as e:
            if not args.ignore_existing:
                usermsg.error(e.message)
                return 1
        return 0

    try:
        module_creator = get_module_creator(module_name, area, fullname)
    except ParsingError as e:
        usermsg.error(e.message)
        return 1

    if export_to_server:
        module_creator.verify_remote_repo()

    module_creator.create_local_module()

    if export_to_server:
        module_creator.push_repo_to_remote()

    msg = module_creator.get_print_message()
    usermsg.info(msg)


def create_empty_remote(area, module_name):
    """Create the module on the server without populating it

    Args:
        area(str): module area (support, python, ...)
        module_name(str): Module name
    """
    server = Server()
    module_path = remove_git_at_end(
        server.dev_module_path(module_name, area=area)
    )
    if server.is_server_repo(module_path):
        raise VerificationError(
            "Module {} already exists on server".format(module_path)
        )
    server.create_remote_repo(module_path)


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
