#!/bin/env dls-python
from pkg_resources import require
require('python-ldap')

import sys
import re
import logging
from dls_ade import vcs_svn
from dls_ade import vcs_git
from dls_ade import dlsbuild
from dls_ade.argument_parser import ArgParser

logging.basicConfig(level=logging.DEBUG)

usage = """
Default <area> is 'support'.
Release <module_name> at version <release> from <area>.
This script will do a test build of the module, and if it succeeds, will create
the release in git. It will then write a build request file to the build
server, causing it to schedule a checkout and build of the git release in
prod.
"""

log_mess = "%s: Released version %s. %s"


def make_parser():
    """
    Takes default parser and adds:
    * module_name
    * release
    * --branch
    * --force
    * --no-test-build
    * --local-build-only
    * --epics_version
    * --message
    * --next_version
    * --git
    * --rhel_version or --windows arguments

    Returns:
        ArgumentParser instance
    """
    parser = ArgParser(usage)

    parser.add_argument(
        "module_name", type=str, default=None,
        help="name of module to release")
    parser.add_argument(
        "release", type=str, default=None,
        help="release number of module to release")
    parser.add_argument(
        "-b", "--branch", action="store", type=str, dest="branch",
        help="Release from a branch BRANCH")
    parser.add_argument(
        "-f", "--force", action="store_true", dest="force", default=None,
        help="force a release. If the release exists in prod it is removed. "
        "If the release exists in svn it is exported to prod, otherwise "
        "the release is created in svn from the trunk and exported to prod")
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
        "-e", "--epics_version", action="store", type=str,
        dest="epics_version",
        help="Change the epics version. This will determine which build "
        "server your job is built on for epics modules. Default is "
        "from your environment")
    parser.add_argument(
        "-m", "--message", action="store", type=str, dest="message",
        default="",
        help="Add user message to the end of the default svn commit message. "
        "The message will be '%s'" %
        (log_mess % ("<module_name>", "<release>", "<message>")))
    parser.add_argument(
        "-n", "--next_version", action="store_true", dest="next_version",
        help="Use the next version number as the release version")
    parser.add_argument(
        "-g", "--git", action="store_true", dest="git",
        help="Release from a git tag from the diamond gitolite repository")

    title = "Build operating system arguments"
    desc = "Note: The following arguments are mutually exclusive - only use one"

    desc_group = parser.add_argument_group(title=title, description=desc)  # Can only add description to group, so have
    group = desc_group.add_mutually_exclusive_group()                      # to nest inside ordinary group

    group.add_argument(
        "-r", "--rhel_version", action="store", type=str,
        dest="rhel_version",
        help="change the rhel version of the build. This will determine which "
        "build server your job is build on for non-epics modules. Default "
        "is from /etc/redhat-release. Can be 6")
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

    # print vars(parser.parse_args())

    return parser


def create_build_object(args):
    """
    Uses parsed arguments to select appropriate build architecture, default is local system os

    Args:
        args(argparse Namespace): Parser arguments

    Returns:
        Either a Windows or RedHat build object
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


def create_vcs_object(module, args):
    """
    Creates either a Git or Svn object depending on flags in args, use module and arguments to construct the objects

    Args:
        module(str): Name of module to be released
        args(argparse Namespace): Parser arguments

    Returns:
        Git or Svn object
    """
    if args.git:
        return vcs_git.Git(module, args)
    else:
        return vcs_svn.Svn(module, args)


def check_parsed_arguments_valid(args,  parser):
    """
    Checks that incorrect arguments invoke parser errors

    Args:
        args(argparse Namespace): Parser arguments
        parser(ArgumentParser: Parser instance

    Raises:
        Error: Module name not specified
        Error: Module version not specified
        Error: Cannot release etc/build or etc/redirector as modules - use configure system instead
        Error: When git is specified, version number must be provided
        Error: args.area area not supported by git
    """
    git_supported_areas = ['support', 'ioc', 'python', 'tools']
    if not args.module_name:
        parser.error("Module name not specified")
        logging.debug(args.module_name)
        logging.debug(args.next_version)
    elif not args.release and not args.next_version:
        parser.error("Module version not specified")
    elif args.area is 'etc' and args.module_name in ['build', 'redirector']:
        parser.error("Cannot release etc/build or etc/redirector as modules"
                     " - use configure system instead")
    elif args.next_version and args.git:
        parser.error("When git is specified, version number must be provided")
    elif args.git and args.area not in git_supported_areas:
        parser.error("%s area not supported by git" % args.area)


def format_argument_version(arg_version):
    """
    Replaces '.' with '-' throughout arg_version to match formatting requirements for log message

    Args:
        arg_version(str): Version tag to be formatted

    Returns:
        Formatted version tag
    """
    return arg_version.replace(".", "-")


def next_version_number(releases, module=None):
    """
    Generates appropriate version number for an incremental release

    Args:
        releases(list): Previous release numbers
        module(str): Name of module to be released

    Returns: Incremented version number

    """
    if len(releases) == 0:
        version = "0-1"
    else:
        last_release = get_last_release(releases)
        version = increment_version_number(last_release)
        if module:
            print "Last release for %s was %s" % (module, last_release)
    return version


def get_last_release(releases):
    """
    Returns the most recent release number

    Args:
        releases(list): Previous release numbers

    Returns: Most recent release number
    """
    from dls_environment import environment
    last_release = environment().sortReleases(releases)[-1].split("/")[-1]
    return last_release


def increment_version_number(last_release):
    """
    Increment the most minor non-zero part of the version number

    Args:
        last_release(str): Most recent previous release number

    Returns:
        Minimally incremented version number
    """
    numre = re.compile("\d+|[^\d]+")
    tokens = numre.findall(last_release)
    for i in reversed(range(0, len(tokens))):
        if tokens[i].isdigit():
            tokens[i] = str(int(tokens[i]) + 1)
            break
    version = "".join(tokens)
    return version


def construct_info_message(module, args, version, build_object):
    """
    Gathers info to display during release

    Args:
        module(str): Module to be released
        args(argparser Namespace): Parser arguments
        version(str): Release version
        build_object(Builder): Either a Windows or RedHat build object

    Returns:
        Info message
    """
    info = str()
    if args.branch:
        btext = "branch %s" % args.branch
    else:
        btext = "trunk"
    info += ('Releasing %s %s from %s, ' % (module, version, btext))
    info += ('using %s build server' % build_object.get_server())
    if args.area in ("ioc", "support"):
        info += (' and epics %s' % build_object.epics())
    return info


def check_epics_version_consistent(module_epics, option_epics, build_epics):
    """
    Checks if epics version is consistent between release and environment, allows user to force build if not consistent

    Args:
        module_epics(str): Epics version of previous release
        option_epics(str): Epics version to change to
        build_epics(str): Epics version of environment

    Returns:
        True if the build can continue, False if not

    """
    build_epics = build_epics.replace("_64", "")
    if not option_epics and module_epics != build_epics:
        question = (
            "You are trying to release a %s module under %s without "
            "using the -e flag. Are you sure [y/n]?" %
            (module_epics, build_epics)).lower()
        answer = ask_user_input(question)
        return True if answer is "y" else False
    else:
        return True


def ask_user_input(question):
    """
    Wrapper for raw_input function

    Args:
        question(str): Question for the user to respond to

    Returns:
        User input

    """
    return raw_input(question)


def get_module_epics_version(vcs):
    """
    Get epics version of most recent release

    Args:
        vcs(Git/Svn): Git or Svn version control system instance

    Returns:
        Epics version of most recent release

    """
    conf_release = vcs.cat("configure/RELEASE")
    module_epics = re.findall(
        r"/dls_sw/epics/(R\d(?:\.\d+)+)/base", conf_release)
    if module_epics:
        module_epics = module_epics[0]
    return module_epics


def perform_test_build(build_object, args, vcs):
    """
    Test build the module and return whether it was successful

    Args:
        build_object(Builder): Either a windows or RedHat builder
        args(argparse Namespace): Parser arguments
        vcs(Git/Svn): Git or Svn version control system instance

    Returns:
        Message to explaining how the test build went, True or False for whether it failed or not
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
        else:
            message += "\nTest build successful."
            if not args.local_build:
                message += " Continuing with build server submission"
    return message, test_fail


def main():

    parser = make_parser()
    args = parser.parse_args()

    check_parsed_arguments_valid(args, parser)
    module = args.module_name

    build = create_build_object(args)
    vcs = create_vcs_object(module, args)

    if args.branch:
        vcs.set_branch(args.branch)

    if args.next_version:
        releases = vcs.list_releases()
        version = next_version_number(releases, module=module)
    else:
        version = format_argument_version(args.release)
    vcs.set_version(version)

    vcs.set_log_message(
        (log_mess % (module, version, args.message)).strip())

    print construct_info_message(module, args, version, build)

    if args.area in ["ioc", "support"]:
        module_epics = get_module_epics_version(vcs)
        sure = check_epics_version_consistent(
            module_epics, args.epics_version, build.epics())
        if not sure:
            sys.exit(0)

    if not args.skip_test:
        test_build_message, test_build_fail = perform_test_build(
            build, args, vcs)
        print test_build_message
        if test_build_fail:
            sys.exit(1)

    if args.local_build:
        sys.exit(0)

    if not vcs.check_version_exists(version) and not args.test_only:
        vcs.release_version(version)

    build.submit(vcs, test=args.test_only)


if __name__ == "__main__":
    main()
