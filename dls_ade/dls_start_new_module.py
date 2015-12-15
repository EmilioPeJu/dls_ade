#!/bin/env dls-python
# This script comes from the dls_scripts python module

from __future__ import print_function

import os
import sys
from dls_ade.argument_parser import ArgParser
import dls_ade.new_module_creator as new_c

usage = """Default <area> is 'support'.
Start a new diamond module of particular type.
Uses makeBaseApp with the dls template for a 'support' or 'ioc' module,\
 copies the example from the environment module for python.
Creates this module and imports it into git.
If the -i flag is used, <module_name> is expected to be of the form "Domain/Technical Area/IOC number" i.e. BL02I/VA/03
The IOC number can be omitted, in which case, it defaults to "01".
If the --fullname flag is used, the IOC will be imported as BL02I/BL02I-VA-IOC-03 (useful for multiple IOCs in the same\
 technical area) and the IOC may optionally be specified as BL02I-VA-IOC-03 instead of BL02I/VA/03
Otherwise it will be imported as BL02I/VA (old naming style)
If the Technical area is BL then a different template is used, to create a top level module for screens and gda."""


def make_parser():

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
    no_import = args.no_import

    mod_c = new_c.get_new_module_creator(module_name, area, fullname)

    mod_c.verify_can_create_local_module()

    if not no_import:
        mod_c.verify_remote_repo()

    mod_c.create_local_module()
    mod_c.print_message()

    if not no_import:
        #mod_c.push_repo_to_remote()
        print("push_repo_to_remote placeholder")
        # I want to test push_repo_to_remote() properly before I uncomment this
    else:
        os.chdir(mod_c.disk_dir)


if __name__ == "__main__":
    #sys.exit(main())
    sys.exit()  # Stops us from running incomplete version!
