#!/bin/env dls-python
# This script comes from the dls_scripts python module
"""
Clone a module, an ioc domain or an entire area of the repository.
When cloning a single module, the branch argument will automatically checkout
the given branch.
"""

import sys
import logging
import json

from dls_ade import vcs_git
from dls_ade.argument_parser import ArgParser
from dls_ade import Server
from dls_ade import logconfig


usage = """
Default <area> is 'support'.
Checkout a module from the <area> area of the repository to the current
directory. If you enter no <module_name>, the whole <area> area will be
checked out.
"""


def make_parser():
    """
    Takes ArgParse instance with default arguments and adds

    Positional Arguments:
        * module_name

    Flags:
        * -b (branch)

    Returns:
        :class:`argparse.ArgumentParser`:  ArgParse instance
    """

    parser = ArgParser(usage)
    parser.add_branch_flag(
        help_msg="Checkout a specific named branch rather than the default"
                 " (master)")

    parser.add_argument("module_name", nargs="?", type=str, default="",
                        help="Name of module")

    return parser


def check_technical_area(area, module):
    """
    Checks if given area is IOC and if so, checks that the module name
    is of the format <domain>/<module> or is not given.

    Args:
        area(str): Area of repository
        module(str): Name of module

    Raises:
        :class:`exception.Exception`: Missing technical area under beamline
    """

    if area == "ioc" and module != "" and len(module.split('/')) < 2:
        raise Exception("Missing Technical Area under Beamline")


def _main():

    log = logging.getLogger(name="dls_ade")
    usermsg = logging.getLogger(name="usermessages")

    parser = make_parser()
    args = parser.parse_args()

    log.info(json.dumps({'CLI': sys.argv, 'options_args': vars(args)}))
    
    if args.module_name == "":
        answer = raw_input("Would you like to checkout the whole " +
                           args.area +
                           " area? This may take some time. Enter Y or N: ")
        if answer.upper() != "Y":
            return

    check_technical_area(args.area, args.module_name)

    module = args.module_name

    server = Server()

    if module == "":
        # Set source to area folder
        source = server.dev_area_path(args.area)
    else:
        # Set source to module in area folder
        source = server.dev_module_path(module, args.area)

    if module == "":
        usermsg.info("Checking out entire {} area".format(args.area))
        server.clone_multi(source)
    elif module.endswith('/') and args.area == 'ioc':
        usermsg.info("Checking out {} technical area...".format(module))
        server.clone_multi(source)
    else:
        usermsg.info("Checking out {module} from {area}".format(module=module,
                                                                area=args.area))
        vcs = server.clone(source, module)

        if args.branch:
            # Get branches list
            branches = vcs_git.list_remote_branches(vcs.repo)
            if args.branch in branches:
                vcs_git.checkout_remote_branch(args.branch, vcs.repo)
            else:
                # Invalid branch name, print branches list and exit
                usermsg.info("Branch '{branch}' does not exist in {source}. "
                             "Leaving clone on default branch. "
                             "Branch List: {branchlist}"
                             .format(branch=args.branch,
                                     source=source,
                                     branchlist=str(branches)))

        vcs_git.add_remotes(vcs.repo, module)


def main():

    # Catch unhandled exceptions and ensure they're logged
    try:
        logconfig.setup_logging(application='dls-checkout-module.py')
        _main()
    except Exception as e:
        logging.exception(e)
        logging.getLogger("usermessages").\
            exception("ABORT: Unhandled exception (see trace below): {}".format(e))
        exit(1)


if __name__ == "__main__":
    main()
