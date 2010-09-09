#!/bin/env dls-python
# This script comes from the dls_scripts python module

usage = """%prog [options] <module_name>

Default <area> is 'support'.
Start a new diamond module of particular type.
Uses makeBaseApp with the dls template for a 'support' or 'ioc' module, copies the example from the environment module for python.
Creates this module and imports it into subversion.
If the -i flag is used, <module_name> is expected to be of the form "Domain/Technical Area/IOC number" i.e. BL02I/VA/03.
The IOC number can be omitted, in which case, it defaults to "01".
If the --fullname flag is used, the IOC will be imported as BL02I/BL02I-VA-IOC-03 (useful for multiple IOCs in the same technical area)
Otherwise it will be imported as BL02I/VA (old naming style)
If the Technical area is BL then a different template is used, to create a top level module for screens and gda."""

import os, sys, shutil

def start_new_module():
    from dls_scripts.options import OptionParser
    parser = OptionParser(usage)
    parser.add_option("-n", "--no_import", action="store_true", dest="no_import", help="Creates the module but doesn't import into svn")
    parser.add_option("-f","--fullname", action="store_true", dest="fullname", help="create new-style ioc, with full ioc name in path")
    (options, args) = parser.parse_args()
    if len(args)!=1:
        parser.error("Incorrect number of arguments.")

    # setup the environment
    module = args[0]
    disk_dir = module
    app_name = module
    cwd = os.getcwd()
    from dls_scripts.svn import svnClient     
    svn = svnClient()

    # Check we know what to do
    if options.area not in ("ioc", "support", "python"):
        raise TypeError, "Don't know how to make a module of type "+options.area

    # setup area
    if options.area == "ioc":
        cols = module.split('/')
        assert len(cols)>1 and cols[1]!='' , 'Missing Technical Area under Domain'
        area = "ioc"
        domain = cols[0]
        technical_area = cols[1]
        if len(cols) == 3 and cols[2]!='':
            ioc_number = cols[2]
        else:
            ioc_number = '01'
        module = domain + "/" + technical_area            
        if technical_area == "BL":
            app_name = domain
        else:
            app_name = domain + '-' + technical_area + '-' + 'IOC' + '-' + ioc_number
            if options.fullname:
                module = domain + "/" + app_name
        disk_dir = module
        # write the message for ioc BL
        BL_message  = '\nPlease now edit '+os.path.join(disk_dir,'/configure/RELEASE')+" to put in correct paths for the ioc\'s other technical areas and path to scripts."
        BL_message += '\nAlso edit '+os.path.join(disk_dir,app_name+'App/src/Makefile')+" to add all database files from these technical areas."
        BL_message += '\nAn example set of screens has been placed in '+os.path.join(disk_dir,app_name+'App/opi/edl')+' . Please modify these.\n'
    elif options.area == "python":
        assert module.startswith("dls_") and "-" not in module and "." not in module, "Python module names must start with 'dls_' and be valid python identifiers"
    dest = svn.devModule(module,options.area)
    if not options.no_import:
        dir_list = [dest,svn.vendorModule(module,options.area),svn.prodModule(module,options.area)]
        if options.area == "ioc":
            dir_list = [ x+"/"+app_name+"App" for x in dir_list ]
        for dir in dir_list:
            assert not svn.pathcheck(dir), "The path "+dir+" already exists in subversion, cannot continue"
    assert not svn.workingCopy(), "Currently in a svn working copy, please move elsewhere and try again"    
    assert not os.path.isdir(disk_dir), "Directory ./"+disk_dir+" already exists, please move elsewhere and try again"
    print 'Making clean directory structure for ' + disk_dir
    os.makedirs(disk_dir)
    os.chdir(disk_dir)
    # write the message for ioc and support modules
    def_message  = '\nPlease now edit '+os.path.join(disk_dir,'/configure/RELEASE')+" to put in correct paths for dependencies."
    def_message += '\nYou can also add dependencies to '+os.path.join(disk_dir,app_name+'App/src/Makefile')
    def_message += '\nand '+os.path.join(disk_dir,app_name+'App/Db/Makefile')+" if appropriate."
    # write the message to python modules
    py_message = "\nPlease add your python files to the "+os.path.join(disk_dir,module)+" directory and edit "+os.path.join(disk_dir,"setup.py")+" appropriately."                
    # make the module in .
    if options.area in ["ioc","support"]:
        if options.area == "ioc":
            if technical_area == "BL":
                os.system('makeBaseApp.pl -t dlsBL ' + app_name)
                print BL_message
            else:
                os.system('makeBaseApp.pl -t dls ' + app_name)
                os.system('makeBaseApp.pl -i -t dls ' + app_name)
                shutil.rmtree(os.path.join(app_name+'App','opi'))        
                print def_message
        else:
            os.system('makeBaseApp.pl -t dls ' + module)
            os.system('dls-make-etc-dir.py && make clean uninstall')
            print def_message            
    elif options.area == "python":
        open("setup.py","w").write("""from setuptools import setup
        
# these lines allow the version to be specified in Makefile.private
import os
version = os.environ.get("MODULEVER", "0.0")
        
setup(
#    install_requires = ['cothread'], # require statements go here
    name = '%s',
    version = version,
    description = 'Module',
    author = '%s',
    author_email = '%s@rl.ac.uk',    
    packages = ['%s'],
#    entry_points = {'console_scripts': ['test-python-hello-world = %s.%s:main']}, # this makes a script
#    include_package_data = True, # use this to include non python files
    zip_safe = False
    )        
""" %(module, os.getlogin(), os.getlogin(), module, module, module))
        open("Makefile","w").write("""# Specify defaults for testing
PREFIX = /dls_sw/prod/tools/RHEL5
PYTHON = $(PREFIX)/bin/python2.6
INSTALL_DIR = /dls_sw/work/common/python/test/packages
SCRIPT_DIR = /dls_sw/work/common/python/test/scripts
MODULEVER = 0.0

# Override with any release info
-include Makefile.private

# This is run when we type make
# It can depend on other targets e.g. the .py files produced by pyuic4 
dist: setup.py $(wildcard %s/*.py)
\tMODULEVER=$(MODULEVER) $(PYTHON) setup.py bdist_egg
\ttouch dist
\t$(MAKE) -C documentation 

# Clean the module
clean:
\t$(PYTHON) setup.py clean
\t-rm -rf build dist *egg-info installed.files
\t-find -name '*.pyc' -exec rm {} \\;
\t$(MAKE) -C documentation clean

# Install the built egg and keep track of what was installed
install: dist
\t$(PYTHON) setup.py easy_install -m \\
\t\t--record=installed.files \\
\t\t--install-dir=$(INSTALL_DIR) \\
\t\t--script-dir=$(SCRIPT_DIR) dist/*.egg        
"""%module)
        os.mkdir(module)
        open(os.path.join(module,module+".py"),"w").write("""def main():
    print "Hello world from %s"
"""%module)            
        open(os.path.join(module,"__init__.py"),"w").write("")
        os.mkdir("documentation")
        open("documentation/Makefile","w").write("""# this is the doxygen output dir
DOCDIR := doxygen

# this is the doxygen executable
DOXYGEN := /dls_sw/work/tools/RHEL5/bin/doxygen

# add the documentation files to the install target
all install: $(DOCDIR)

# rule for documentation
$(DOCDIR): config.cfg manual.src
\tmkdir -p $(DOCDIR)
\t$(DOXYGEN) config.cfg

# Remove entire documentation/doxygen dir on clean
clean:
\trm -rf $(DOCDIR
""")        
        open("documentation/index.html","w").write("""<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
<html>
<head>
<title>Documentation</title>
<!-- This tag redirects to the doxygen index -->
<meta http-equiv="REFRESH" content="0;url=doxygen/index.html"></HEAD>
<body/>
</html>
""")
        open("documentation/config.cfg","w").write("""# info about project
PROJECT_NAME           = %(module)s
PROJECT_NUMBER         = 
# use <module>.<func> instead of <module>::<func>
OPTIMIZE_OUTPUT_JAVA   = YES
# need this to get all function/variable docs
SHOW_NAMESPACES        = YES
# add the input dir
INPUT                 += ../%(module)s .
# add some examples
# EXAMPLE_PATH           = examples
# add the extensions
FILE_PATTERNS          = *.py manual.src
# don't warn on undocumented elements
QUIET                  = YES
# where to output to
OUTPUT_DIRECTORY       = doxygen
# where to find images
# IMAGE_PATH             = images
# create a search engine
SEARCHENGINE           = YES
# make class diagrams
CLASS_DIAGRAMS         = YES
# don't make latex output
GENERATE_LATEX         = NO
# put html in .
HTML_OUTPUT            = .
# include sources
SOURCE_BROWSER         = YES
# make everything, even if no doc strings
EXTRACT_ALL            = YES
""" % locals())
        open("documentation/manual.src","w").write(r"""/**
\mainpage %(module)s Python Module
\section intro_sec Introduction
I'm going to describe the module here, possibly with a <a href="http://www.google.co.uk">web link to the manufacturers webpage</a>. \n
You can also link to \ref %(module)s.py "internally generated documentation" with alternate text, or by just by mentioning its name, e.g. %(module)s.py

\section Installation

Type make && make install

\section Usage

I'm going to describe how to use the module here
*/
""" % locals())

        print py_message

    if not options.no_import:
    # import the module into svn
        os.chdir(cwd)
        print 'Importing ' + disk_dir + ' into ' + dest
        svn.import_( disk_dir, dest, 'Initial structure of new ' + disk_dir, recurse=True )
        shutil.rmtree(disk_dir)
        print 'Checkout ' + disk_dir + ' from ' + dest
        svn.checkout( dest, disk_dir)
        user = os.getlogin()
        if options.area == "python":
            svn.propset("svn:ignore","dist\nbuild\ninstalled.files\n",disk_dir)        
        elif options.area in ("support", "ioc"):
            svn.propset("svn:ignore","bin\ndata\ndb\ndbd\ninclude\nlib\n",disk_dir)    
        svn.propset("dls:contact",user,disk_dir)
        svn.checkin(disk_dir,module+": changed contact and set svn:ignore")

if __name__ == "__main__":
    sys.exit(start_new_module())
