#!/bin/env dls-python2.6
# This script comes from the dls_scripts python module

usage = """%prog [options] <module_name> <module_release>

Default <area> is 'support'.
This script removes all O.* directories from an old release of a module and
tars it up before deleting the release directory. <module_name>/<module_release>
will be stored as <module_name>/<module_release>.tar.gz. Running the script with
a -u flag will untar the module and remove the archive.
"""

import os, sys

def archive_module():
    from dls_environment import environment
    e = environment()
    from dls_scripts.options import OptionParser
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
    
    # create test build filename
    user = os.getlogin()    
    ev = e.epicsVer()
    out_dir = "/dls_sw/work/etc/build/queue"   
    #out_dir = "/tmp"
    filename = "%(action)s-%(module)s-%(release)s-%(ev)s-%(user)s.sh5" % locals()
    filename = os.path.join(out_dir, filename.replace("/", "_"))
    
    # Send the build script
    if options.untar:
        assert os.path.isfile(archive), "Archive '%s' doesn't exist" % archive
        assert not os.path.isdir(release_dir), "Path '%s' already exists" % release_dir        
        command = "tar -xzpf '%(archive)s' -C '%(w_dir)s' &&\nrm %(archive)s" % locals()  
    else:
        assert os.path.isdir(release_dir), "Path '%s' doesn't exist" % release_dir
        assert not os.path.isfile(archive), "Archive '%s' already exists" % archive
    	command = ""
    	dirs = ("O.linux-x86", "O.linux-arm", "O.vxWorks-ppc604_long", "O.win32-x86", "O.Common")
    	for d in dirs:
    		 command += "find '%(release_dir)s' -name '%(d)s' -prune -exec rm -rf {} \; &&\n" % locals()        
        command += "tar -czf '%(archive)s' -C '%(w_dir)s' '%(release)s' &&\nrm -rf '%(release_dir)s'" % locals()
    archive_script = """#!/usr/bin/env bash
__run_job()
{
    TEMP_LOG="$(mktemp)"
    trap 'rm -f "$TEMP_LOG"' EXIT
    {
        {
        
%(command)s

        } || echo Job failed with rc $?
    } >"$TEMP_LOG" 2>&1
    if (($(stat -c%%s "$TEMP_LOG") != 0 || 0)); then
        {
            echo dls-archive-module.py %(action)s failed creating output:
            echo
            cat "$TEMP_LOG"
        } |
            mail -s 'dls-archive-module.py %(action)s failure' %(user)s@rl.ac.uk
    fi
}
__run_job &
""" %locals()

    # create the build request
    open(os.path.join(filename),"w").write(archive_script)
    print "%s request file created: '%s'" %(action.title(), filename)
    print "%(module)s %(release)s will be %(action)sd by the build server shortly" %locals()
    
if __name__ == "__main__":
    sys.exit(archive_module())
