#!/bin/env dls-python
from pkg_resources import require
require('dls_environment')
require('python-ldap')

import os
import sys
import re
import vcs_svn
import vcs_git
import dlsbuild
from dls_environment.options import OptionParser
from optparse import OptionGroup

usage = """%prog [options] <module_name> <release_#>

Default <area> is 'support'.
Release <module_name> at version <release_#> from <area>.
This script will do a test build of the module, and if it succeeds, will create
the release in svn. It will then write a build request file to the build
server, causing it to schedule a checkout and build of the svn release in
prod."""


# set default variables
log_mess = "%s: Released version %s. %s"


def make_parser():
    ''' helper method containing options and help text
    '''

    parser = OptionParser(usage)
    parser.add_option(
        "-b", "--branch", action="store", type="string", dest="branch",
        help="Release from a branch BRANCH")
    parser.add_option(
        "-f", "--force", action="store_true", dest="force",
        help="force a release. If the release exists in prod it is removed. "
        "If the release exists in svn it is exported to prod, otherwise "
        "the release is created in svn from the trunk and exported to prod")
    parser.add_option(
        "-t", "--no-test-build", action="store_true", dest="skip_test",
        help="If set, this will skip the local test build "
        "and just do a release")
    parser.add_option(
        "-l", "--local-build-only", action="store_true", dest="local_build",
        help="If set, this will only do the local test build and no more.")
    parser.add_option(
        "-T", "--test_build-only", action="store_true", dest="test_only",
        help="If set, this will only do a test build on the build server")
    parser.add_option(
        "-W", "--work_build", action="store_true", dest="work_build",
        help="If set, this will do a test build on the build server "
             "in the modules work area")
    parser.add_option(
        "-e", "--epics_version", action="store", type="string",
        dest="epics_version",
        help="Change the epics version. This will determine which build "
        "server your job is built on for epics modules. Default is "
        "from your environment")
    parser.add_option(
        "-m", "--message", action="store", type="string", dest="message",
        default="",
        help="Add user message to the end of the default svn commit message. "
        "The message will be '%s'" %
        (log_mess % ("<module_name>", "<release_#>", "<message>")))
    parser.add_option(
        "-n", "--next_version", action="store_true", dest="next_version",
        help="Use the next version number as the release version")
    parser.add_option(
        "-g", "--git", action="store_true", dest="git",
        help="Release from a git tag from the diamond gitolite repository")

    group = OptionGroup(
        parser, "Build operating system options",
        "Note: The following options are mutually exclusive - only use one")
    group.add_option(
        "-r", "--rhel_version", action="store", type="string",
        dest="rhel_version",
        help="change the rhel version of the build. This will determine which "
        "build server your job is build on for non-epics modules. Default "
        "is from /etc/redhat-release. Can be 4,5,5_64")
    group.add_option(
        "-w", "--windows", action="store", dest="windows",
        help="Release the module or IOC only for the Windows version. "
        "Note that the windows build server can not create a test build. "
        "A configure/RELEASE.win32-x86 or configure/RELEASE.windows64 file"
        " must exist in the module in order for the build to start. "
        "If the module has already been released with the same version "
        "the build server will rebuild that release for windows. "
        "Existing unix builds of the same module version will not be "
        "affected. Can be 32 or 64")
    parser.add_option_group(group)

    return parser


def create_build_object(options):
    ''' Uses parsed options to select appropriate build architecture, default is
    local system os
    '''
    if options.rhel_version:
        build_object = dlsbuild.RedhatBuild(
            options.rhel_version,
            options.epics_version)
    elif options.windows:
        build_object = dlsbuild.WindowsBuild(
            options.windows,
            options.epics_version)
    else:
        build_object = dlsbuild.default_build(
            options.epics_version)

    build_object.set_area(options.area)
    build_object.set_force(options.force)

    return build_object


def create_vcs_object(module, options):
    ''' specific vcs class depends on flags in options, use module and options
    to construct the objects
    '''
    if options.git:
        return vcs_git.Git(module, options)
    else:
        return vcs_svn.Svn(module, options)


def check_parsed_options_valid(args, options, parser):
    '''All checks that invoke parser errors.'''
    git_supported_areas = ['support', 'ioc', 'python']
    if len(args) < 1:
        parser.error("Module name not specified")
    elif len(args) < 2 and not options.next_version:
        parser.error("Module version not specified")
    elif options.area is 'etc' and args[0] in ['build', 'redirector']:
        parser.error("Cannot release etc/build or etc/redirector as modules"
                     " - use configure system instead")
    elif options.next_version and options.git:
        parser.error("When git is specified, version number must be provided")
    elif options.git and options.area not in git_supported_areas:
        parser.error("%s area not supported by git" % options.area)


def format_argument_version(arg_version):
    ''' helper method formatting version taken from command line arguments
    '''
    return arg_version.replace(".", "-")


def next_version_number(releases, module=None):
    ''' return appropriate version number for an incremental release
    '''
    if len(releases) == 0:
        version = "0-1"
    else:
        last_release = get_last_release(releases)
        version = increment_version_number(last_release)
        if module:
            print "Last release for %s was %s" % (module, last_release)
    return version


def get_last_release(releases):
    ''' from a list of strings, return the latest version number
    '''
    from dls_environment import environment
    last_release = environment().sortReleases(releases)[-1].split("/")[-1]
    return last_release


def increment_version_number(last_release):
    ''' increment the most minor non-zero part of the version number
    '''
    numre = re.compile("\d+|[^\d]+")
    tokens = numre.findall(last_release)
    for i in reversed(range(0, len(tokens))):
        if tokens[i].isdigit():
            tokens[i] = str(int(tokens[i]) + 1)
            break
    version = "".join(tokens)
    return version


def construct_info_message(module, options, version, build_object):
    ''' helper method gathering info to a string to display during release
    '''
    info = str()
    if options.branch:
        btext = "branch %s" % options.branch
    else:
        btext = "trunk"
    info += ('Releasing %s %s from %s, ' % (module, version, btext))
    info += ('using %s build server' % build_object.get_server())
    if options.area in ("ioc", "support"):
        info += (' and epics %s' % build_object.epics())
    return info


def check_epics_version_consistent(module_epics, option_epics, build_epics):
    build_epics = build_epics.replace("_64","")
    if not option_epics and module_epics != build_epics:
        question = ("You are trying to release a %s module under %s without "
            "using the -e flag. Are you sure [y/n]?" %
            (module_epics, build_epics)).lower()
        answer = ask_user_input(question)
        return True if answer is "y" else False
    else:
        return True


def ask_user_input(question):
    return raw_input(question)


def get_module_epics_version(vcs):
    conf_release = vcs.cat("configure/RELEASE")
    module_epics = re.findall(
        r"/dls_sw/epics/(R\d(?:\.\d+)+)/base", conf_release)
    if module_epics:
        module_epics = module_epics[0]
    return module_epics


def perform_test_build(build_object, options, vcs):

    message = ''
    test_fail = False

    if not build_object.local_test_possible():
        message += "Local test build not possible since local system not the same "
        message += "OS as build server"
    else:
        message += "Performing test build on local system"
        if build_object.test(vcs) != 0:
            test_fail = True
        else:
            message += "\nTest build successful."
            if not options.local_build:
                message += " Continuing with build server submission"
    return message, test_fail


def main():

    parser = make_parser()
    options, args = parser.parse_args()

    check_parsed_options_valid(args, options, parser)
    module = args[0]

    build = create_build_object(options)
    vcs = create_vcs_object(module, options)

    if options.branch:
        vcs.set_branch(options.branch)

    if options.next_version:
        releases = vcs.list_releases()
        version = next_version_number(releases, module=module)
    else:
        version = format_argument_version(args[1])
    vcs.set_version(version)

    vcs.set_log_message(
        (log_mess % (module, version, options.message)).strip())

    print construct_info_message(module, options, version, build)

    if options.area in ["ioc", "support"]:
        module_epics = get_module_epics_version(vcs)
        sure = check_epics_version_consistent(
            module_epics, options.epics_version, build.epics())
        if not sure:
            sys.exit(0)

    if not options.skip_test:
        test_build_message, test_build_fail = perform_test_build(
            build, options, vcs)
        print test_build_message
        if test_build_fail:
            sys.exit(1)

    if options.local_build:
        sys.exit(0)

    if not vcs.check_version_exists(version) and not options.test_only:
        vcs.release_version(version)

    test = "work" if options.work_build else options.test_only

    build.submit(vcs, test=True)


if __name__ == "__main__":
    main()
