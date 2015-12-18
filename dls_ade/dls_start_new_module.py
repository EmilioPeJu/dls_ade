#!/bin/env dls-python
# This script comes from the dls_scripts python module

from __future__ import print_function

import os
import sys
from dls_ade.argument_parser import ArgParser
import dls_ade.new_module_creator as new_c

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
         "module for screens and gda."
         "\nIf the template-folder optional argument is given, the module "
         "will be created using the given folder as a template. It is able "
         "to use {module_name:s}, {get_login:s}, and for IOC or support "
         "modules {app_name:s} to insert the module name, user login and "
         "application name (phrase before 'App' in support and IOC modules), "
         "respectively. This can be used in both folders and text files."
         "\nIf the --template-update flag is used, the template folder will "
         "update the existing template dictionary, as opposed to overwriting "
         "it.")


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
    parser.add_argument(
        "-t", "--template-folder", action="store", type=str,
        default=None, dest="template_folder",
        help="New modules will use this as the template directory")
    parser.add_argument(
        "-u", "--template-update", action="store_true", dest="template_update",
        help=("Will update the original module templates"
              " as opposed to overwriting them"))

    return parser


def main():

    parser = make_parser()
    args = parser.parse_args()

    module_name = args.module_name
    area = args.area
    fullname = args.fullname
    no_import = args.no_import
    template_folder = args.template_folder
    template_update = args.template_update

    nmc_obj = new_c.get_new_module_creator(module_name, area, fullname)

    nmc_obj.verify_can_create_local_module()

    if not no_import:
        nmc_obj.verify_remote_repo()

    if template_folder:
        nmc_obj.set_template_files_from_folder(template_folder,
                                               template_update)

    nmc_obj.create_local_module()
    nmc_obj.print_message()

    if not no_import:
        #nmc_obj.push_repo_to_remote()
        print("push_repo_to_remote placeholder")
        # I want to test push_repo_to_remote() properly before I uncomment this
    else:
        os.chdir(nmc_obj.disk_dir)


if __name__ == "__main__":
    #sys.exit(main())
    sys.exit()  # Stops us from running incomplete version!
