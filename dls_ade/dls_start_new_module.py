#!/bin/env dls-python
# This script comes from the dls_scripts python module

from __future__ import print_function

import os
import sys
from dls_ade.argument_parser import ArgParser
from dls_ade.get_module_creator import get_module_creator

usage = ("Default <area> is 'support'."
         "\nStart a new diamond module of a particular type."
         "\nUses makeBaseApp with the dls template for a 'support' or 'ioc' "
         "module, and uses the default templates in new_module_templates for "
         "both Python and Tools modules."
         "\nCreates this module and imports it into git."
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
    Returns default parser with additional, module-specific arguments.

    The additional parser arguments are:
        - module_name
        - --no-import
        - --fullname.

    Returns:
        An ArgumentParser instance with additional arguments
    """
    parser = ArgParser(usage)
    parser.add_argument(
        "module_name", type=str, default=None,
        help="name of module")
    parser.add_argument(
        "-n", "--no-import", action="store_true", dest="no_import",
        help="Creates the module but doesn't import into svn")
    parser.add_argument(
        "-f", "--fullname", action="store_true", dest="fullname",
        help="create new-style ioc, with full ioc name in path")

    return parser


def main():

    parser = make_parser()
    args = parser.parse_args()

    module_name = args.module_name
    area = args.area
    fullname = args.fullname
    export_to_server = not args.no_import

    module_creator = get_module_creator(module_name, area, fullname)

    module_creator.verify_can_create_local_module()

    if export_to_server:
        module_creator.verify_remote_repo()

    module_creator.create_local_module()
    module_creator.print_message()

    if export_to_server:
        module_creator.push_repo_to_remote()
    else:
        os.chdir(module_creator.disk_dir)


if __name__ == "__main__":
    # sys.exit(main())
    sys.exit()  # Stops us from running incomplete version!
