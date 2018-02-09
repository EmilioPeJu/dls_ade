#!/bin/env dls-python
# This script comes from the dls_scripts python module
"""
List the branches of a module on the repository.
"""

import sys
import shutil
import logging

from dls_ade.argument_parser import ArgParser
from dls_ade import path_functions as pathf
from dls_ade import vcs_git, Server
from dls_ade import logconfig

usage = """
Default <area> is 'support'.
List the branches of <module_name> in the <area> area of the repository.
"""


def make_parser():
    """
    Takes ArgParse instance with default arguments and adds

    Positional Arguments:
        * module_name

    Returns:
        :class:`argparse.ArgumentParser`:  ArgParse instance
    """

    parser = ArgParser(usage)
    parser.add_module_name_arg()
    return parser


def _main():
    log = logging.getLogger(name="dls_ade")
    usermsg = logging.getLogger(name="usermessages")
    log.info("application: %s: arguments: %s", sys.argv[0], sys.argv)

    parser = make_parser()
    args = parser.parse_args()

    pathf.check_technical_area(args.area, args.module_name)

    server = Server()

    source = server.dev_module_path(args.module_name, args.area)

    vcs = server.temp_clone(source)

    branches = vcs_git.list_remote_branches(vcs.repo)
    usermsg.info("Branches of {module}: {branches}"
                 .format(module=source, branches=", ".join(branches)))

    shutil.rmtree(vcs.repo.working_tree_dir)


def main():
    # Catch unhandled exceptions and ensure they're logged
    try:
        logconfig.setup_logging(application='dls-list-branches.py')
        _main()
    except Exception as e:
        logging.exception(e)
        logging.getLogger("usermessages").exception("ABORT: Unhandled exception (see trace below): {}".format(e))
        exit(1)


if __name__ == "__main__":
    main()
