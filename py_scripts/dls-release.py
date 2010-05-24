#!/bin/env dls-python
# This script comes from the dls_scripts python module

usage = """%prog [options] <module_name> <release_#>

Default <area> is 'support'.
Release <module_name> at version <release_#> from <area>.
This script will do a test build of the module, and if it succeeds, will create the release in svn. It will then write a build request file to the build server, causing it to schedule a checkout and build of the svn release in prod.
If run using the area "init", "svn update" will be updated in /dls_sw/prod/etc/init"""

import os, subprocess, sys, time, re
from subprocess import call

def release():
    "script for releasing modules"
    
    # override epics_version if set
    from dls_environment import environment    
    e = environment()
    epics_version = e.epicsVer()
    
    # work out rhel version
    rhel_text = open("/etc/redhat-release").read()
    rhel_version = re.findall(r"release (\d*)(.\d*)?", rhel_text)
    assert rhel_version, "Cannot parse /etc/redhat-release for rhel version"
    rhel_version = int(rhel_version[0][0])
    
    # find out which user wants to release
    user = os.getlogin()
        
    # set default variables
    out_dir = "/dls_sw/work/etc/build/queue/"
    test_dir = "/dls_sw/work/etc/build/test/"+"_".join([str(x) for x in time.localtime()[:6]])+"_"+user
    svn_mess = "%s: Released version %s. %s"

    # command line options  
    from dls_scripts.options import OptionParser    
    parser = OptionParser(usage)
    parser.add_option("-b", "--branch", action="store", type="string", 
        dest="branch", help="Release from a branch BRANCH")
    parser.add_option("-f", "--force", action="store_true", dest="force", 
        help="force a release. If the release exists in prod it is removed. " \
            "If the release exists in svn it is exported to prod, otherwise " \
            "the release is created in svn from the trunk and exported to prod")
    parser.add_option("-t", "--test_build", action="store_true", dest="test", 
        help="If set, this will skip the test build and just do a release")
    parser.add_option("-e", "--epics_version", action="store", type="string", 
        dest="epics_version", 
        help="Change the epics version. This will determine which build " \
            "server your job is built on for epics modules. Default is %s " \
            "(from your environment)" % e.epicsVer())
    parser.add_option("-r", "--rhel_version", action="store", type="string", 
        dest="rhel_version", 
        help="change the rhel version of the build. This will determine which "\
            "build server your job is build on for non-epics modules. Default "\
            "is %d (from /etc/redhat-release)" % rhel_version)    
    parser.add_option("-m", "--message", action="store", type="string", 
        dest="message", 
        help="Add user message to the end of the default svn commit message. " \
            "The message will be '%s'" % \
            (svn_mess%("<module_name>","<release_#>","<message>")))
    parser.add_option("-w", "--windows", action="store_true", dest="windows", 
        default=False,
        help="Release the module or IOC only for the Windows platform. " \
            "Note that the windows build server can not create a test build. " \
            "A configure/RELEASE.win32-x86 file must exist in the module in " \
            "in order for the build to start. " \
            "If the module has already been released with the same version " \
            "the build server will rebuild that release for windows. " \
            "Existing unix builds of the same module version will not be "\
            "affected.")


    (options, args) = parser.parse_args()    

    # set epics version, and extension
    if options.epics_version:
        if e.epics_ver_re.match(options.epics_version):
            e.setEpics(options.epics_version)
        else:
            parser.error("Expected epics version like R3.14.8.2, got '%s'" % \
                options.epics_version)

    # override rhel version
    if options.rhel_version:
        rhel_version = int(options.rhel_version)

    # set postfix
    if options.area in ["support", "ioc"]:
        if e.epicsVer() in ["R3.14.11"]:
            postfix = ".sh5"
            rhel_version = 5
        else:
            postfix = ".sh"
            rhel_version = 4
    else:
        if rhel_version > 4:
            postfix = ".sh%d" % rhel_version
        else:
            postfix = ".sh"

    # if area is init, just update the relevant part of prod
    if options.area in ["init", "build_scripts"]:
        if options.area == "init":
            print "Updating background process initialisation in prod..."
            path = out_dir+"prod_etc_init_update_"+user+postfix
            os.system('echo "svn update /dls_sw/prod/etc/init && make -C /dls_sw/prod/etc/init" > '+path)
        if options.area=="build_scripts":
            if len(args)!=1:
                parser.error("Releasing tools: 1 argument, tool name")
            print "Updating tools"
            path = out_dir+"tool_"+args[0]+"_"+user+postfix
            command = "svn update /dls_sw/prod/tools/RHEL5/build_scripts && /dls_sw/prod/tools/RHEL5/build_scripts/build_program %s" % args[0]
            if os.listdir("/dls_sw/work/targetOS/tar-files"):
                command = "mv /dls_sw/work/targetOS/tar-files/* /dls_sw/prod/targetOS/tar-files && " + command
            os.system('echo "%s" > %s'%(command, path))            
        print "Update request file created: "+path
        print "Request will be executed by the build server shortly"
        sys.exit()        

    if len(args)!=2:
        parser.error("Incorrect number of arguments.")

    # set variables
    module = args[0]
    release_number = args[1].replace(".","-")
        
    # print messages
    if options.branch:
        btext = "branch %s" % options.branch
    else:
        btext = "trunk"
    print 'Releasing %s %s from %s, using RHEL%s build server'%(module,release_number,btext,rhel_version),
    if options.area in ("ioc","support"):
        print "and epics %s" % e.epicsVer(),
    print        

    # import svn client
    from dls_scripts.svn import svnClient    
    svn = svnClient()
    if options.message is None:
        options.message = ""
    svn.setLogMessage((svn_mess%(module,release_number,options.message)).strip())
    
    # setup svn directories
    if options.branch:
        src_dir = os.path.join(svn.branchModule(module,options.area),options.branch)
    else:
        src_dir = svn.devModule(module,options.area)
    rel_dir = svn.prodModule(module,options.area)
    
    # check for existence of directories    
    assert svn.pathcheck(src_dir),src_dir+' does not exist in the repository.'
        
    directories = (out_dir, test_dir, src_dir, rel_dir)
    if options.windows == True:
        assert options.area in ["support","ioc"], \
            "Windows build can only be done for areas 'support' and 'ioc'\n"\
            "\t\tAborting release."
        windowsbuild( svn, options, module, release_number, e, directories )
    else:
        # check if release is in prod
        prodDir = os.path.join(e.prodArea(options.area),module,release_number)
        assert options.force or not os.path.isdir(prodDir), \
        module+" "+release_number+" already exists in "+prodDir
        unixbuild( svn, options, module, release_number, e, directories, postfix )

    
            
def unixbuild(svn, options, module, release_number, env, directories, postfix):
    out_dir, test_dir, src_dir, rel_dir = directories
    user = os.getlogin()
    
    # do a test build and create the release if the release isn't in subversion
    if not svn.pathcheck(os.path.join(rel_dir, release_number)):
        if not options.test:
            # check out to test area
            while os.path.isdir(test_dir):
                test_dir += "_1"
            print "Doing test build, logging in "+ os.path.join(test_dir,src_dir.split("/")[-1])+"/build.log ..."
            os.mkdir(test_dir)
            os.chdir(test_dir)
            os.system("rm -rf "+src_dir.split("/")[-1])
            os.system("svn co "+src_dir+" > /dev/null")
            os.chdir(src_dir.split("/")[-1])
            # check python files look right
            if options.area == "python" and postfix != ".sh":
                assert "Makefile.private" in open("Makefile").read(), "New build system no longer hacks setup.py. You need to include Makefile.private in your Makefile. See the ADE for more details."
            if os.path.isfile("./configure/RELEASE"):
                os.system("mv configure/RELEASE configure/RELEASE.svn")
                os.system("""sed -e 's,^ *EPICS_BASE *=.*$,'"EPICS_BASE=/dls_sw/epics/"""+env.epicsVer()+"""/base," -e 's,^ *SUPPORT *=.*$,'"SUPPORT=/dls_sw/prod/"""+env.epicsVer()+"""/support," -e 's,^ *WORK *=.*$,'"#WORK=commented out to prevent prod modules depending on work modules," configure/RELEASE.svn > configure/RELEASE""")
            success = call('. /dls_sw/etc/profile && make &> build.log', 
                shell=True, env={'DLS_EPICS_RELEASE': env.epicsVer()})
            assert success == 0, "Module will not build. Please check module does not depend on work"
            os.chdir("../..")
            os.system("rm -rf "+test_dir)
            print "Test build successful, continuing with release"

        # copy the source to the release directory
        svn.mkdir(rel_dir)
        svn.copy(src_dir,os.path.join(rel_dir, release_number))
        print "Created release in svn directory: "+os.path.join(rel_dir,release_number)
    
    # temporary hack to make it work for R3.13.9
    if env.epicsVer() == "R3.13.9":
        path = os.path.join("/home/diamond/R3.13.9/prod",options.area,module)
        if not os.path.isdir(path):
            os.system("mkdir -p "+path)
        os.chdir(path)
        assert not os.path.isdir(release_number), "Release already exists in prod"
        os.system("svn co "+rel_dir+"/"+release_number+" > /dev/null")
        os.chdir(release_number)
        os.system('make')
        print "Release has been made in: "+os.getcwd() 
        sys.exit()
    
    # in script: checkout svn module
    build_script = """#!/usr/bin/env bash

# Script for building a diamond production module.
epics_version="""+env.epicsVer()+"""
svn_dir="""+rel_dir.replace(svn.root(),"http://serv0002.cs.diamond.ac.uk/repos/controls")+"""
build_dir="""+env.prodArea(options.area)+"/"+module+"""
version="""+release_number+r"""

# Set up environment
DLS_EPICS_RELEASE=$epics_version
DLS_DEV=1
source /dls_sw/etc/profile
SVN_ROOT=%s

# Checkout module
mkdir -p $build_dir                     || { echo Can not mkdir $build_dir; exit 1; }
cd $build_dir                           || { echo Can not cd to $build_dir; exit 1; }
rm -rf $version                         || { echo Can not rm $version; exit 1; }
svn checkout $svn_dir/$version          || { echo Can not check out  $svn_dir/$version; exit 1; }
cd $version                             || { echo Can not cd to $version; exit 1; }

# Write some history
dls-logs-since-release.py -r --area=%s %s > DEVHISTORY.autogen
"""%("http://serv0002.cs.diamond.ac.uk/repos/controls",options.area,module)

    # if we're looking at a support or ioc module then edit its configure/RELEASE to remove references to work
    if options.area in ["support","ioc"]:
        build_script += r"""
# Modify configure/RELEASE
if [ -e "configure/RELEASE" ]; then
    mv configure/RELEASE configure/RELEASE.svn || { echo Can not rename configure/RELEASE; exit 1; }
    sed -e 's,^ *EPICS_BASE *=.*$,'"EPICS_BASE=/dls_sw/epics/$epics_version/base,"   \
        -e 's,^ *SUPPORT *=.*$,'"SUPPORT=/dls_sw/prod/$epics_version/support," \
        -e 's,^ *WORK *=.*$,'"#WORK=commented out to prevent prod modules depending on work modules," \
    configure/RELEASE.svn > configure/RELEASE  || { echo Can not edit configure/RELEASE; exit 1; }
fi"""

    # if its a python module pass setup.py the version
    elif options.area == "python":
        if postfix == ".sh":
            # old rhel 4 way
            build_script += r"""
# Modify setup.py
mv setup.py setup.py.svn || { echo Can not move setup.py to setup.py.svn; exit 1; }
echo '# The following line was added by the release script' >> setup.py || { echo Can not edit setup.py; exit 1; }
echo -e "version = '"""+release_number.replace("-",".")+r"""'" >> setup.py || { echo Can not edit setup.py; exit 1; }
cat setup.py.svn >> setup.py || { echo Can not edit setup.py; exit 1; }"""
        else:
            # new way with Makefile.private
            build_script += r"""
# Add Makefile.private
echo '# Overrides for release info
PREFIX = /dls_sw/prod/tools/RHEL5
PYTHON=$(PREFIX)/bin/python2.6
INSTALL_DIR=$(PREFIX)/lib/python2.6/site-packages
SCRIPT_DIR=$(PREFIX)/bin
MODULEVER = %s' > Makefile.private || { echo Cannot write to Makefile.private; exit 1; }
"""%release_number.replace("-",".")
            
    # setup the command to run
    if options.area=="python":
        command = "(make && make install)"
    else:
        command = "make"
        
    # do the build
    build_script += r"""
# Build
timestamp=$(date +%%Y%%m%%d-%%H%%M%%S)
error_log=build_${timestamp}.err
build_log=build_${timestamp}.log
{
    %(command)s 4>&1 1>&3 2>&4 |
    tee $error_log
} >$build_log 3>&1
if [ $(stat -c%%s $error_log) -ne 0 ] ; then
    cat $error_log | mail -s 'Build Errors: %(module)s %(release_number)s' %(user)s@rl.ac.uk
elif [ -e documentation/Makefile ]; then 
    make -C documentation
fi
 """ % locals()

    # Finally create the file with the build job/script
    # The build server itself will take care of the rest
    createbuildjob(module, release_number, directories, build_script, postfix = postfix)

def windowsbuild(svn, options, module, release_number, env, directories):
    out_dir, test_dir, src_dir, rel_dir = directories
    user = os.getlogin()
    
    assert env.epicsVer() in ("R3.14.10","R3.14.11"), \
        "Only epics versions R3.14.10 and R3.14.11 is supported for the Windows platform"
        
    assert options.area in ("support","ioc"), \
        "Only areas 'support' and 'ioc' are not supported under Windows."

    # Check whether a configure/RELEASE.win32-x86 exist in the modules repository.
    assert svn.pathcheck(os.path.join(src_dir, "configure/RELEASE.win32-x86")),\
        "The module does not contain a configure/RELEASE.win32-x86 file which "\
        "is required for building on the windows platform. \nPlease create "\
        "this file with the windows paths for EPICS_BASE and SUPPORT."

    # create the release if the release is not in subversion already
    if not svn.pathcheck(os.path.join(rel_dir, release_number)):
        # copy the source to the release directory
        svn.mkdir(rel_dir)
        svn.copy(src_dir,os.path.join(rel_dir, release_number))
        print "Created release in svn directory: "+os.path.join(rel_dir,release_number)

    # Import the Windows batch script template and substitute all the relevant macros
    script = winbuildscript
    script = script.replace("$(DLS_EPICS_RELEASE)", env.epicsVer())
    script = script.replace("$(AREA)", options.area)
    script = script.replace("$(MODULE)", module)
    script = script.replace("$(VERSION)", release_number)
    createbuildjob(module, release_number, directories, script, prefix = "_".join([str(x) for x in time.localtime()[:6]])+"release", postfix = ".bat")

def createbuildjob(module, release_number, directories, build_script, prefix="release", postfix = ".sh"):
    out_dir, test_dir, src_dir, rel_dir = directories
    user = os.getlogin()
    
    # generate the filename
    filename = "-".join([prefix,module,release_number,user+postfix])
    filename = filename.replace("/","_")

    # check filename isn't already in use
    while os.path.isfile(filename):
        filename = filename.replace(postfix,"_1"+postfix)

    # create the build request
    f = open(os.path.join(out_dir,filename),"w")
    f.write( build_script )
    f.close()
    print "Build request file created: "+os.path.join(out_dir,filename)
    print module+" "+release_number+" will be exported and built by the build server shortly"
    if postfix == ".bat":
        print "Note that Windows build logs are NOT emailed to you automatically. You must check the completion of the build manually by reading the build log and checking whether the module was build succesfully."
        print "The build log will appear once the build has completed in: /dls_sw/prod/etc/build/complete/"+filename+".log"

# Template batch script to checkout and build a released
# module in W:\prod\...
#
# This template will be used by the linux dls-release.py 
# scripts to create a build job that can be executed by
# the build server as a scheduled job when dumped in the 
# build servers work queue.
#
# Usage: Substitute the various macros, defined as: $(MACRO)
# The macros will identify module name, version, area and 
# EPICS environment -all things needed to identify a particular
# released module, it's version and build environment.
#
# Ulrik Pedersen 14-07-2009

winbuildscript = r"""
@rem ---------------------------------------------------------
@rem Release build script
@rem module: $(MODULE) version: $(VERSION)
@rem EPICS version: $(DLS_EPICS_RELEASE)
@rem area: '$(AREA)'
@rem -----------------------------------------------------------

set DLS_EPICS_RELEASE=$(DLS_EPICS_RELEASE)
set _area=$(AREA)
set _module=$(MODULE)
set _version=$(VERSION)

set _profile=W:\etc\profile.bat
set _svn_root=http://serv0002.cs.diamond.ac.uk/repos/controls/diamond/release/%_area%
set _dlsprod=W:\prod\%DLS_EPICS_RELEASE%\%_area%\%_module%\%_version%

@rem Configure the environment by loading a profile.
@rem The profile is responsible to set up the build environment:
@rem  - Path to compiler, linker and all necessary environment setup
@rem  - Path to subversion svn commands
@rem  - path to minGW make tool
@rem  - EPICS_BASE and other related EPICS environment variables.
if exist %_profile% (
    call %_profile%
) else (
    echo ### ERROR [%TIME%] ### Could not find profile. Aborting build.
    exit /B 1
)

if not exist %_dlsprod% (
    echo Creating directory %_dlsprod%
    mkdir %_dlsprod%
    if not %ErrorLevel%==0 (
        echo ### ERROR [%TIME%] ### Unable to create directory: %_dlsprod%
        echo                        Aborting build.
        exit /B %ErrorLevel%
    )
    cd %_dlsprod%
    svn checkout  %_svn_root%/%_module%/%_version% .
    if not %ErrorLevel%==0 (
        echo ### ERROR [%TIME%] ### Unable to access subversion repository. Aborting build.
        exit /B %ErrorLevel%
    )
) else (
    echo Module has already been released for this version.
    cd %_dlsprod%
)

echo Performing Windows build using mingw32-make.
mingw32-make clean
mingw32-make

"""


if __name__ == "__main__":
    sys.exit(release())
