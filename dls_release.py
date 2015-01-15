#!/bin/env dls-python
import os
import sys
import re
import vcs_svn
import dlsbuild

usage = """%prog [options] <module_name> <release_#>

Default <area> is 'support'.
Release <module_name> at version <release_#> from <area>.
This script will do a test build of the module, and if it succeeds, will create
the release in svn. It will then write a build request file to the build
server, causing it to schedule a checkout and build of the svn release in
prod."""


# set default variables
log_mess = "%s: Released version %s. %s"


def release(module, version, options):
    """script for releasing modules"""

    # Create build object for version
    if options.rhel_version:
        build = dlsbuild.RedhatBuild(
            options.rhel_version,
            options.epics_version)
    elif options.windows:
        build = dlsbuild.WindowsBuild(options.windows, options.epics_version)
    else:
        build = dlsbuild.default_build(options.epics_version)
    build.set_area(options.area)
    build.set_force(options.force)

    if options.git:
        # vcs = vcs_svn.Svn()
        raise NotImplementedError("git support not implemented yet, go away")
    else:
        vcs = vcs_svn.Svn()

    if options.next_version:
        releases = vcs.list_releases(module, options.area)
        if len(releases) == 0:
            version = "0-1"
        else:
            from dls_environment import environment
            last_release = environment().sortReleases(releases)[-1]. \
                split("/")[-1]
            print "Last release for %s was %s" % (module, last_release)
            numre = re.compile("\d+|[^\d]+")
            tokens = numre.findall(last_release)
            for i in range(0, len(tokens), -1):
                if tokens[i].isdigit():
                    tokens[i] = str(int(tokens[i]) + 1)
                    break
            version = "".join(tokens)

    vcs.set_log_message(
        (log_mess % (module, version, options.message)).strip())

    src_dir = vcs.get_src_dir(module, options)
    rel_dir = vcs.get_rel_dir(module, options, version)

    print "src_dir =", src_dir
    print "rel_dir =", rel_dir

    assert vcs.path_check(src_dir), \
        src_dir + ' does not exist in the repository.'

    # print messages
    if options.branch:
        btext = "branch %s" % options.branch
    else:
        btext = "trunk"
    print 'Releasing %s %s from %s, using %s build server' % \
        (module, version, btext, build.get_server()),
    if options.area in ("ioc", "support"):
        print "and epics %s" % build.epics(),
    print

    # check if we really meant to release with this epics version
    if options.area in ["ioc", "support"]:
        conf_release = vcs.cat(src_dir+"/configure/RELEASE")
        module_epics = re.findall(r"/dls_sw/epics/(R\d(?:\.\d+)+)/base",
                                  conf_release)
        if module_epics:
            module_epics = module_epics[0]
        build_epics = build.epics().replace("_64","")
        if not options.epics_version and module_epics != build_epics:
            sure = raw_input(
                "You are trying to release a %s module under %s without "
                "using the -e flag. Are you sure [y/n]?" %
                (module_epics, build_epics)).lower()
            if sure != "y":
                sys.exit()

    print "terminating here for testing purposes, after epics version check"
    sys.exit(0)        

    # If this release already exists, test from the release directory, not the
    # trunk.
    if vcs.path_check(rel_dir):
        src_dir = rel_dir

    # Do the test build
    if not options.skip_test:
        if not build.local_test_possible():
            print "Local test build not possible since local system not " \
                  "the same OS as build server"
        else:
            print "Performing test build on local system"

            if build.test(src_dir, module, version) != 0:
                sys.exit(1)

            if not options.local_build:
                print "Test build successful, " \
                      "continuing with build server submission"

    if options.local_build:
        sys.exit(0)

    # Copy the source to the release directory in subversion
    if src_dir != rel_dir and not options.test_only:
        vcs.checkout_module(module, options.area, src_dir, rel_dir)
        src_dir = rel_dir
        print "Created release in svn directory: " + rel_dir

    test = "work" if options.work_build else options.test_only

    # Submit the build job
    build.submit(rel_dir, module, version, test=test)


def main():
    # Parse command line options
    from dls_environment.options import OptionParser
    from optparse import OptionGroup
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

    options, args = parser.parse_args()
    print "options: ", options, "args: ", args

    # set variables - the first is a bit of a backwards compatible hack, for
    # now.
    if len(args) < 1:
        parser.error("Module name not specified")
    else:
        module = args[0]

    if options.area == "etc" and module in ["build", "redirector"]:
        parser.error("Cannot release etc/build or etc/redirector as modules"
                     " - use configure system instead")

    if options.next_version:
        version = None
    elif len(args) < 2:
        parser.error("Module version not specified")
    else:
        version = args[1].replace(".", "-")

    release(module, version, options)

if __name__ == "__main__":
    main()
