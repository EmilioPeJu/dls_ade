#!/bin/env dls-python
# This script comes from the dls_scripts python module

usage = """%prog [options] <module_name> <module_release>

Default <area> is 'support'.
This script removes all O.* directories from an old release of a module and
tars it up before deleting the release directory. <module_name>/<module_release>
will be stored as <module_name>/<module_release>.tar.gz. Running the script with
a -u flag will untar the module and remove the archive.
"""

import os, sys

def tar_module():
    from dls_environment import environment
    e = environment()
    from dls_environment.options import OptionParser
    parser = OptionParser(usage)
    parser.add_option("-u", "--untar", action="store_true", dest="untar", help="Untar archive created with dls-archive-module.py")
    parser.add_option("-e", "--epics_version", action="store", type="string", dest="epics_version", help="change the epics version, default is "+e.epicsVer()+" (from your environment)")    
    
    # parse args
    (options, args) = parser.parse_args()    
    if len(args)!=2:
        parser.error("Incorrect number of arguments.")
    module = args[0]
    release = args[1]
    if options.untar:
        action = "unarchive"
    else:
        action = "archive"
    
    # check correct area
    assert options.area in ("support", "ioc", "python", "matlab"), \
        "Modules in area '%s' cannot be archived" % options.area

    # setup the environment
    if options.epics_version:
        if e.epics_ver_re.match(options.epics_version):
            e.setEpics(options.epics_version)
        else:
            parser.error("Expected epics version like R3.14.8.2, got: "+options.epics_version)
    if options.area == "ioc":
        assert len(module.split('/'))>1, 'Missing Technical Area under Beamline'
    
    # Check for the existence of release of this module/IOC    
    w_dir = os.path.join(e.prodArea(options.area), module)
    
    # If an archive already exists fail
    release_dir = os.path.join(w_dir, release)
    archive = release_dir + ".tar.gz"

    if options.untar:
        assert os.path.isfile(archive), "Archive '%s' doesn't exist" % archive
        assert not os.path.isdir(release_dir), "Path '%s' already exists" % release_dir        
    else:
        assert os.path.isdir(release_dir), "Path '%s' doesn't exist" % release_dir
        assert not os.path.isfile(archive), "Archive '%s' already exists" % archive
    
    # Create build object for release
    import dls_release.dlsbuild as dlsbuild
    build=dlsbuild.archive_build( options.untar )
    
    if options.epics_version:
        build.set_epics(options.epics_version)
    
    build.set_area( options.area )

    build.submit( "", module, release )
    
if __name__ == "__main__":
    sys.exit(tar_module())
