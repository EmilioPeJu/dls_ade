#!/bin/env dls-python2.6
# This script comes from the dls_scripts python module

usage = """%prog [options] <module_name> <release_#>

Default <area> is 'support'.
Release <module_name> at version <release_#> from <area>.
This script will do a test build of the module, and if it succeeds, will create
the release in svn. It will then write a build request file to the build server,
causing it to schedule a checkout and build of the svn release in prod.
If run using the area "init", "svn update" will be updated in
/dls_sw/prod/etc/init"""

import os, sys, re

# set default variables
svn_mess = "%s: Released version %s. %s"

def release(module, version, options):
    """script for releasing modules"""
    import dls_scripts.dlsbuild as dlsbuild

    # Import svn client and initialise it
    from dls_scripts.svn import svnClient
    svn = svnClient()

    # Generate a next minor version number, if required
    if options.next_version:
        import pysvn
        release_paths = []
        source = svn.prodModule(module, options.area)
        for node, _ in svn.list(source, depth=pysvn.depth.immediates)[1:]:
            release_paths.append(os.path.basename(node.path))

        if len(release_paths) == 0:
            version = "0-1"
        else:
            from dls_environment import environment
            last_release = environment().sortReleases(release_paths)[-1]. \
                split("/")[-1]
            print "Last release for %s was %s"%(module, last_release)

            numre = re.compile("(.*)(\d+)([^\d/]*)$")
            match = numre.match(last_release).groups()
            version = "%s%d%s"%(match[0], int(match[1])+1, match[2])

    if options.message is None:
        options.message = ""

    svn.setLogMessage((svn_mess%(module, version, options.message)).strip())

    # setup svn directories
    if options.branch:
        src_dir = os.path.join(
            svn.branchModule(module, options.area), options.branch)
    else:
        src_dir = svn.devModule(module, options.area)

    rel_dir = os.path.join(svn.prodModule(module, options.area), version)

    # Create build object for version
    if options.rhel_version:
        build = dlsbuild.redhat_build(options.rhel_version)
    elif options.windows:
        build = dlsbuild.windows_build(options.windows)
    else:
        build = dlsbuild.default_build()

    if options.epics_version:
        build.set_epics(options.epics_version)

    build.set_area(options.area)
    build.set_force(options.force)

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

    # check for existence of directories
    assert svn.pathcheck(src_dir), src_dir+' does not exist in the repository.'

    # check if we really meant to release with this epics version
    if options.area in ["ioc", "support"]:
        os.system("svn export " + src_dir +
                  "/configure/RELEASE /tmp/RELEASE > /dev/null")
        if os.path.isfile("/tmp/RELEASE"):
            text = open("/tmp/RELEASE").read()
            os.system("rm -rf /tmp/RELEASE")
            module_epics = \
                re.findall(r"/dls_sw/epics/(R\d(?:\.\d+)+)/base", text)
            if module_epics:
                module_epics = module_epics[0]
            if not options.force and module_epics != build.epics():
                sure = raw_input(
                    "You are trying to release a %s module under %s without "
                    "using the -e flag. Are you sure [y/n]?" %
                    (module_epics, build.epics())).lower()
                if sure != "y":
                    sys.exit()

    # If this release already exists, test from the release directory, not the
    # trunk.
    if svn.pathcheck(rel_dir):
        src_dir = rel_dir

    # Do the test build
    if not options.skip_test:
        if dlsbuild.default_build().get_server() != build.get_server():
            print "Local test build not possible since local system not " \
                  "the same OS as build server"
        else:
            print "Performing test build on local system"

            if build.test(src_dir, module, version) != 0:
                sys.exit(1)

            print "Test build successful, " \
                  "continuing with build server submission"

    if options.local_build:
        sys.exit(0)

    # Copy the source to the release directory in subversion
    if src_dir != rel_dir and not options.test_only:
        svn.mkdir(rel_dir)
        svn.copy(src_dir, os.path.join(rel_dir, version))
        src_dir = rel_dir
        print "Created release in svn directory: " + \
            os.path.join(rel_dir, version)

    test = "work" if options.work_build else options.test_only

    # Submit the build job
    build.submit(src_dir, module, version, test=test)


if __name__ == "__main__":
    # Parse command line options
    from dls_scripts.options import OptionParser
    from optparse import OptionGroup
    parser = OptionParser(usage)
    parser.add_option("-b", "--branch", action="store", type="string",
        dest="branch", help="Release from a branch BRANCH")
    parser.add_option("-f", "--force", action="store_true", dest="force",
        help="force a release. If the release exists in prod it is removed. "
            "If the release exists in svn it is exported to prod, otherwise "
            "the release is created in svn from the trunk and exported to prod")
    parser.add_option("-t", "--no-test-build",
        action="store_true", dest="skip_test",
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
    parser.add_option("-e", "--epics_version", action="store", type="string",
        dest="epics_version",
        help="Change the epics version. This will determine which build "
            "server your job is built on for epics modules. Default is "
            "from your environment")
    parser.add_option("-m", "--message", action="store", type="string",
        dest="message",
        help="Add user message to the end of the default svn commit message. "
            "The message will be '%s'" %
            (svn_mess % ("<module_name>", "<release_#>", "<message>")))
    parser.add_option(
        "-n", "--next_version", action="store_true", dest="next_version",
        help="Use the next version number as the release version")

    group = OptionGroup(
        parser, "Build operating system options",
        "Note: The following options are mutually exclusive - only use one")
    group.add_option("-r", "--rhel_version", action="store", type="string",
        dest="rhel_version",
        help="change the rhel version of the build. This will determine which "
            "build server your job is build on for non-epics modules. Default "
            "is from /etc/redhat-release. Can be 4,5,5_64")
    group.add_option("-w", "--windows", action="store", dest="windows",
        help="Release the module or IOC only for the Windows version. "
            "Note that the windows build server can not create a test build. "
            "A configure/RELEASE.win32-x86 or configure/RELEASE.windows64 file "
            "must exist in the module in order for the build to start. "
            "If the module has already been released with the same version "
            "the build server will rebuild that release for windows. "
            "Existing unix builds of the same module version will not be "
            "affected. Can be 32 or 64")
    parser.add_option_group(group)

    options, args = parser.parse_args()

    # set variables - the first is a bit of a backwards compatible hack, for
    # now.
    if len(args) < 1:
        parser.error("Module name not specified")
    else:
        module = args[0]

    if options.next_version:
        version = None
    elif len(args) < 2:
        parser.error("Module version not specified")
    else:
        version = args[1].replace(".", "-")

    release(module, version, options)
