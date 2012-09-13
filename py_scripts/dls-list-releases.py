#!/bin/env dls-python2.6
# This script comes from the dls_scripts python module

usage = """%prog [options] <module_name>

Default <area> is 'support'.
List the releases of a module in the release area of <area>. By default uses
the epics release number from your environment to work out the area on disk to
look for the module, this can be overridden with the -e flag.
"""

import os, sys

def list_releases():
    from dls_environment import environment
    e = environment()    
    from dls_scripts.options import OptionParser    
    parser = OptionParser(usage)
    parser.add_option("-l", "--latest", action="store_true", dest="latest", help="Only print the latest release")
    parser.add_option("-s", "--svn", action="store_true", dest="svn", help="Print releases available in svn")
    parser.add_option("-e", "--epics_version", action="store", type="string", dest="epics_version", help="change the epics version, default is "+e.epicsVer()+" (from your environment)")
    (options, args) = parser.parse_args()
    if len(args)!=1:
        parser.error("Incorrect number of arguments.")

    # setup the environment
    module = args[0]
    if options.epics_version:
        if e.epics_ver_re.match(options.epics_version):
            e.setEpics(options.epics_version)
        else:
            parser.error("Expected epics version like R3.14.8.2, got: "+options.epics_version)
    if options.area == "ioc":
        assert len(module.split('/'))>1, 'Missing Technical Area under Beamline'

    # Force options.svn if no releases in the file system
    if options.area in ["etc", "build_scripts", "epics"]:
        options.svn = True
        
    # Check for the existence of releases of this module/IOC    
    release_paths = []    
    if options.svn:
        from dls_scripts.svn import svnClient 
        svn = svnClient()
        import pysvn
        source = os.path.join(svn.prodArea(options.area), module)
        for node, _ in svn.list(source, depth=pysvn.depth.immediates)[1:]:
            release_paths.append(os.path.basename(node.path))
    else:
        release_dir = os.path.join(e.prodArea(options.area), module)
        if os.path.isdir(release_dir):        
            for p in os.listdir(release_dir):
                if os.path.isdir(os.path.join(release_dir, p)):
                    release_paths.append(p)

    # check some releases have been made
    if len(release_paths) == 0:
        if options.svn:
            msg = "No releases made in svn"
        else:
            msg = "No releases made for %s" % options.epics_version
        print "%s: %s" % (module, msg)
        return 1

    # sort the releases        
    release_paths = e.sortReleases(release_paths)
    if options.latest:
        print release_paths[-1].split("/")[-1]
    else:
        for path in release_paths:
            print path.split("/")[-1]

if __name__ == "__main__":
    sys.exit(list_releases())
