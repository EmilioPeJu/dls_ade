#!/bin/env dls-python

"""
Release a module with a specified release version from the repository.
This script will do a test build of the module, and if it succeeds, will create
the release in git. It will then write a build request file to the build
server, causing it to schedule a checkout and build of the git release in prod.
The branch flag will create the release from a branch of the module instead of
master. The no-test-build flag will skip the test build and release the module
anyway. The local build only flag will just run a test build and say whether it
was successful or not. The message flag will add to the default commit message
for the release. The next-version flag will set the version as the minimal
increment of the previous release. The git flag will create the release from
the server
"""

import sys
import re
import logging
import logconfig

from dls_ade import Server
from dls_ade import dlsbuild
from dls_ade.argument_parser import ArgParser
from dls_ade.dls_environment import environment
from dls_ade.exceptions import VCSGitError

usage = """
Default <area> is 'support'.
Release <module_name> at version <release> from <area>.
This script will do a test build of the module, and if it succeeds, will create
the release in git. It will then write a build request file to the build
server, causing it to schedule a checkout and build of the git release in
prod.
"""


def make_parser():
    """
    Takes ArgParse instance with default arguments and adds

    Positional Arguments:
        * module_name
        * release

    Flags:
        * -b (branch)
        * -f (force)
        * -t (no-test-build)
        * -l (local-build-only)
        * -e (epics_version)
        * -T (test_build_only
        * -m (message)
        * -n (next_version)
        * -r (rhel_version) or --w (windows arguments)

    Returns:
        :class:`argparse.ArgumentParser`: ArgParse instance

    """
    parser = ArgParser(usage)

    parser.add_module_name_arg()
    parser.add_release_arg()
    parser.add_branch_flag(
        help_msg="Release from a branch")
    parser.add_epics_version_flag(
        help_msg="Change the epics version. This will determine which build "
                 "server your job is built on for epics modules. Default is "
                 "from your environment")

    parser.add_argument(
        "-f", "--force", action="store_true", dest="force", default=None,
        help="force a release. If the release exists in prod it is removed. "
        "If the release exists in git it is exported to prod, otherwise "
        "the release is created in git and exported to prod")
    parser.add_argument(
        "-t", "--no-test-build", action="store_true", dest="skip_test",
        help="If set, this will skip the local test build "
        "and just do a release")
    parser.add_argument(
        "-l", "--local-build-only", action="store_true", dest="local_build",
        help="If set, this will only do the local test build and no more.")
    parser.add_argument(
        "-T", "--test_build-only", action="store_true", dest="test_only",
        help="If set, this will only do a test build on the build server")
    parser.add_argument(
        "-m", "--message", action="store", type=str, dest="message",
        default="",
        help="Add user message to the end of the default commit message. "
        "The message will be <module_name>: Released version <release>."
        "<message>")
    parser.add_argument(
        "-n", "--next_version", action="store_true", dest="next_version",
        help="Use the next version number as the release version")

    title = "Build operating system arguments"
    desc = "Note: The following arguments are mutually exclusive - only use" \
           "one"

    # Can only add description to group, so have to nest inside ordinary group
    desc_group = parser.add_argument_group(title=title, description=desc)
    group = desc_group.add_mutually_exclusive_group()

    group.add_argument(
        "-r", "--rhel_version", action="store", type=str,
        dest="rhel_version",
        help="change the rhel version of the build. This will determine which "
        "build server your job is build on for non-epics modules. Default "
        "is from /etc/redhat-release. Can be 6 or 7")
    group.add_argument(
        "-w", "--windows", action="store", dest="windows", type=str,
        help="Release the module or IOC only for the Windows version. "
        "Note that the windows build server can not create a test build. "
        "A configure/RELEASE.win32-x86 or configure/RELEASE.windows64 file"
        " must exist in the module in order for the build to start. "
        "If the module has already been released with the same version "
        "the build server will rebuild that release for windows. "
        "Existing unix builds of the same module version will not be "
        "affected. Must specify 32 or 64 after the flag to choose 32/64-bit. "
        "Both 32 and 64 bit builds are built on the same 64-bit build server")

    return parser


def create_build_object(args):
    """
    Uses parsed arguments to select appropriate build architecture, default is
    local system os

    Args:
        args(:class:`argparse.Namespace`): Parser arguments

    Returns:
        :class:`~dls_ade.dlsbuild.Builder`: Either a Windows or RedHat build
            object

    """
    if args.rhel_version:
        build_object = dlsbuild.RedhatBuild(
            args.rhel_version,
            args.epics_version)
    elif args.windows:
        build_object = dlsbuild.WindowsBuild(
            args.windows,
            args.epics_version)
    else:
        build_object = dlsbuild.default_build(
            args.epics_version)

    build_object.set_area(args.area)
    build_object.set_force(args.force)

    return build_object


def check_parsed_arguments_valid(args, parser):
    """
    Checks that incorrect arguments invoke parser errors

    Args:
        args(:class:`argparse.Namespace`): Parser arguments
        parser(:class:`argparse.ArgumentParser`): Parser instance

    Raises:
        :class:`dls_ade.exceptions.VCSGitError`:
            * Module name not specified
            * Module version not specified
            * Cannot release etc/build or etc/redirector as modules - use
                configure system instead
            * When git is specified, version number must be provided
            * <args.area> area not supported by git

    """
    git_supported_areas = ['support', 'ioc', 'python', 'matlab', 'tools', 'targetOS']
    if not args.module_name:
        parser.error("Module name not specified")
        logging.debug(args.module_name)
        logging.debug(args.next_version)
    elif not args.release and not args.next_version:
        parser.error("Module version not specified")
    elif args.area is 'etc' and args.module_name in ['build', 'redirector']:
        parser.error("Cannot release etc/build or etc/redirector as modules"
                     " - use configure system instead")
    elif args.next_version:
        parser.error("When git is specified, version number must be provided")
    elif args.area not in git_supported_areas:
        parser.error("%s area not supported by git" % args.area)


def format_argument_version(arg_version):
    """
    Replaces '.' with '-' throughout arg_version to match formatting
    requirements for log message

    Args:
        arg_version(str): Version tag to be formatted

    Returns:
        str: Formatted version tag

    """
    return arg_version.replace(".", "-")


def next_version_number(releases, module=None):
    """
    Generates appropriate version number for an incremental release

    Args:
        releases(list of str): Previous release numbers
        module(str): Name of module

    Returns:
        str: Incremented version number

    """
    if len(releases) == 0:
        version = "0-1"
    else:
        last_release = get_last_release(releases)
        version = increment_version_number(last_release)
        if module:
            logging.getLogger(name="usermessages").info("Last release for {module} was {last_release}"
                                                        .format(module=module, last_release=last_release))
    return version


def get_last_release(releases):
    """
    Returns the most recent release number

    Args:
        releases(list of str): Previous release numbers

    Returns:
        str: Most recent release number

    """
    last_release = environment().sortReleases(releases)[-1].split("/")[-1]
    return last_release


def increment_version_number(last_release):
    """
    Increment the most minor non-zero part of the version number

    Args:
        last_release(str): Most recent previous release number

    Returns:
        str: Minimally incremented version number

    """
    numre = re.compile("\d+|[^\d]+")
    tokens = numre.findall(last_release)
    for i in reversed(range(0, len(tokens))):
        if tokens[i].isdigit():
            tokens[i] = str(int(tokens[i]) + 1)
            break
    version = "".join(tokens)
    return version


def construct_info_message(module, branch, area, version, build_object):
    """
    Gathers info to display during release

    Args:
        module(str): Module to be released
        branch(str): Branch to be released
        area(str): Area of module
        version(str): Release version
        build_object(:class:`~dls_ade.dlsbuild.Builder`): Either a Windows or
            RedHat build object

    Returns:
        str: Info message for user

    """
    info = str()
    if branch:
        btext = "branch {}".format(branch)
    else:
        btext = "tag: {}".format(version)
    info += ('{module} {version} from {btext}, '.format(
        module=module, version=version, btext=btext))
    info += ('using {} build server'.format(build_object.get_server()))
    if area in ("ioc", "support"):
        info += (' and epics {}'.format(build_object.epics()))
    return info


def check_epics_version_consistent(module_epics, option_epics, build_epics):
    """
    Checks if epics version is consistent between release and environment,
    allows user to force build if not consistent

    Args:
        module_epics(str): Epics version of previous release
        option_epics(str): Epics version to change to
        build_epics(str): Epics version of environment

    Returns:
        bool: True if the build can continue, False if not

    """
    build_epics = build_epics.replace("_64", "")
    if not option_epics and module_epics != build_epics:
        question = (
            "You are trying to release a %s module under %s without "
            "using the -e flag. Are you sure [Y/N]?" %
            (module_epics, build_epics)).lower()
        answer = ask_user_input(question)
        return False if answer.upper() is not "Y" else True
    else:
        return True


def ask_user_input(question):
    """
    Wrapper for raw_input function

    Args:
        question(str): Question for the user to respond to

    Returns:
        str: User input

    """
    return raw_input(question)


def get_module_epics_version(vcs):
    """
    Get epics version of most recent release

    Args:
        vcs(:class:`~dls_ade.vcs_git.Git`): Git version control system instance


    Returns:
        str: Epics version of most recent release

    """
    conf_release = vcs.cat("configure/RELEASE")
    module_epics = re.findall(
        r"/dls_sw/epics/(R\d(?:\.\d+)+)/base", conf_release)
    if module_epics:
        module_epics = module_epics[0]
    return module_epics


def perform_test_build(build_object, local_build, vcs):
    """
    Test build the module and return whether it was successful

    Args:
        build_object(:class:`~dls_ade.dlsbuild.Builder`): Either a windows or
            RedHat builder instance
        local_build(bool): Specifier to perform test build only
        vcs(:class:`~dls_ade.vcs_git.Git`): Git version control system instance

    Returns:
        str, bool: Message explaining how the test build went, True or False
            for whether it failed or not

    """
    message = ''
    test_fail = False

    if not build_object.local_test_possible():
        message += "Local test build not possible since local system not the "
        message += "same OS as build server"
    else:
        message += "Performing test build on local system"
        if build_object.test(vcs) != 0:
            test_fail = True
            message += "\nTest build failed."
        else:
            message += "\nTest build successful."
            if not local_build:
                message += " Continuing with build server submission"
    return message, test_fail


def _main():
    log = logging.getLogger(name="dls_ade")
    usermsg = logging.getLogger(name="usermessages")

    log.info("application: %s: arguments: %s", sys.argv[0], sys.argv)
    parser = make_parser()
    args = parser.parse_args()

    check_parsed_arguments_valid(args, parser)
    module = args.module_name

    build = create_build_object(args)

    server = Server()
    source = server.dev_module_path(module, args.area)
    vcs = server.temp_clone(source)

    if args.branch:
        vcs.set_branch(args.branch)

    if args.next_version:
        releases = vcs.list_releases()
        version = next_version_number(releases, module=module)
    else:
        version = format_argument_version(args.release)

    try:
        vcs.set_version(version)
    except VCSGitError as err:
        log.exception(err)
        usermsg.error("Aborting: {msg}".format(msg=err))
        sys.exit(1)

    if args.area in ["ioc", "support"]:
        module_epics = get_module_epics_version(vcs)
        if module_epics:
            sure = check_epics_version_consistent(
                module_epics, args.epics_version, build.epics())
            if not sure:
                usermsg.info("Cancelling: EPICS version not consistent")
                sys.exit(0)

    if not args.skip_test:
        test_build_message, test_build_fail = perform_test_build(
            build, args.local_build, vcs)
        usermsg.info(test_build_message)
        if test_build_fail:
            usermsg.error("Aborting: local test build failed")
            sys.exit(1)

    if args.local_build:
        usermsg.info("Done. Local test build only.")
        sys.exit(0)

    msg_build_job = "test-release" if args.test_only else "Release"
    msg_create_build_job = "Creating {buildjob} job for {info_msg}".format(
        buildjob=msg_build_job,
        info_msg=construct_info_message(module, args.branch, args.area, version, build))
    usermsg.info(msg_create_build_job)

    build.submit(vcs, test=args.test_only)
    usermsg.info("{build_job} job for {area}-module: \'{module}\' {version} submitted to build server queue".format(
        build_job=msg_build_job, area=args.area, module=module, version=str(version)))


def main():
    # Catch unhandled exceptions and ensure they're logged
    try:
        logconfig.setup_logging(application='dls-release.py')
        _main()
    except Exception as e:
        logging.exception(e)
        logging.getLogger("usermessages").exception("ABORT: Unhandled exception (see trace below): {}".format(e))
        exit(1)


if __name__ == "__main__":
    main()
