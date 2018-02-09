#!/bin/env dls-python
# This script comes from the dls_scripts python module

import sys
import shutil
import logging

from dls_ade.argument_parser import ArgParser
from dls_ade import path_functions as pathf
from dls_ade import vcs_git
from dls_ade import Server
from dls_ade import logconfig

usage = """
Default <area> is 'support'.
Check if a module in the <area> area of the repository has had changes
committed since its last release.
"""


def make_parser():
    """
    Takes default parser arguments and adds module_name

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

    module = args.module_name
    source = server.dev_module_path(module, args.area)
    log.debug(source)

    if server.is_server_repo(source):
        vcs = server.temp_clone(source)
        releases = vcs_git.list_module_releases(vcs.repo)

        if releases:
            last_release_num = releases[-1]
        else:
            usermsg.info("No release has been done for {}".format(module))
            # return so last_release_num can't be referenced before assignment
            return 1
    else:
        raise IOError("{} does not exist on the repository.".format(source))

    # Get a single log between last release and HEAD
    # If there is one, then changes have been made
    logs = list(vcs.repo.iter_commits(last_release_num + "..HEAD",
                                      max_count=1))
    if logs:
        usermsg.info("Changes have been made to {module}"
                     " since release {release}".format(module=module, release=last_release_num))
    else:
        usermsg.info("No changes have been made to {module}"
                     " since most recent release {release}".format(module=module, release=last_release_num))

    shutil.rmtree(vcs.repo.working_tree_dir)


def main():
    # Catch unhandled exceptions and ensure they're logged
    try:
        logconfig.setup_logging(application='dls-changes-since-release.py')
        _main()
    except Exception as e:
        logging.exception(e)
        logging.getLogger("usermessages").exception("ABORT: Unhandled exception (see trace below): {}".format(e))
        exit(1)


if __name__ == "__main__":
    main()
