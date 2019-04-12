#!/bin/env dls-python
# This script comes from the dls_scripts python module
"""
List the modules of an area or ioc domain on the repository
"""

import os
import sys
import json
import logging

from dls_ade.argument_parser import ArgParser
from dls_ade.dls_utilities import remove_git_at_end
from dls_ade import Server
from dls_ade import logconfig

usage = """
Default <area> is 'support'.
List all modules in the <area> area.
If <dom_name> given and <area> = 'ioc', list the subdirectories of <dom_name>.
e.g. %prog -p prints: converter, cothread, dls_nsga, etc.
"""


def make_parser():
    """
    Takes ArgParse instance with default arguments and adds

    Flags:
        * -d (domain) :class:`argparse.ArgumentParser`

    Returns:
        :class:`argparse.ArgumentParser`: Parser instance
    """
    parser = ArgParser(usage)
    parser.add_argument("domain_name", nargs="?", type=str,
                        help="domain of ioc to list")
    return parser


def get_module_list(source):
    """
    Prints the modules in the area of the repository specified by source.

    Args:
        source(str): Suffix of URL to list from e.g. controls/ioc/BL15I
        area(str): area to filter search by e.g. ioc
    Returns:
        list: List of modules (list of str)
    """
    server = Server()
    repos = server.get_server_repo_list(source)
    modules = [remove_git_at_end(p.split(source + '/')[-1]) for p in repos]
    return modules


def _main():
    log = logging.getLogger(name="dls_ade")
    usermsg = logging.getLogger(name="usermessages")

    parser = make_parser()
    args = parser.parse_args()

    log.info(json.dumps({'CLI': sys.argv, 'options_args': vars(args)}))

    server = Server()

    if args.area == "ioc" and args.domain_name:
        search_area = os.path.join(args.area, args.domain_name)
        source = server.dev_group_path(args.domain_name, args.area)
    else:
        search_area = args.area
        source = server.dev_area_path(args.area)

    usermsg.info("Listing modules in the %s area\n"
                 "Hold on, this may take a little while ...",
                 search_area)
    module_list = sorted(get_module_list(source))
    print_msg = "Modules in {area}:\n".format(area=search_area)
    print_msg += "\n".join(module_list)
    usermsg.info(print_msg)


def main():
    # Catch unhandled exceptions and ensure they're logged
    try:
        logconfig.setup_logging(application='dls-list-modules.py')
        _main()
    except Exception as e:
        logging.exception(e)
        logging.getLogger("usermessages").exception(
            "ABORT: Unhandled exception (see trace below): {}".format(e)
        )
        exit(1)


if __name__ == "__main__":
    main()
