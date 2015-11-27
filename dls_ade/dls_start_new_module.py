#!/bin/env dls-python
# This script comes from the dls_scripts python module

from __future__ import print_function

import os
import sys
import shutil
from argument_parser import ArgParser
import path_functions as pathf
from new_module_templates import py_files, tools_files, support_ioc_files


usage = """Default <area> is 'support'.
Start a new diamond module of particular type.
Uses makeBaseApp with the dls template for a 'support' or 'ioc' module,\
 copies the example from the environment module for python.
Creates this module and imports it into git.
If the -i flag is used, <module_name> is expected to be of the form "Domain/Technical Area/IOC number" i.e. BL02I/VA/03
The IOC number can be omitted, in which case, it defaults to "01".
If the --fullname flag is used, the IOC will be imported as BL02I/BL02I-VA-IOC-03 (useful for multiple IOCs in the same\
 technical area) and the IOC may optionally be specified as BL02I-VA-IOC-03 instead of BL02I/VA/03
Otherwise it will be imported as BL02I/VA (old naming style)
If the Technical area is BL then a different template is used, to create a top level module for screens and gda."""


def make_parser():

    parser = ArgParser(usage)
    parser.add_argument(
        "module_name", type=str, default=None,
        help="name of module")
    parser.add_argument(
        "-n", "--no_import", action="store_true", dest="no_import",
        help="Creates the module but doesn't import into svn")
    parser.add_argument(
        "-f", "--fullname", action="store_true", dest="fullname",
        help="create new-style ioc, with full ioc name in path")

    return parser

def make_files_python(module):
    ''' Creates the files necessary for a python module '''
    format_vars = {'module':module, 'getlogin':os.getlogin()}

    open("setup.py", "w").write(py_files['setup.py'].format(**format_vars))
    open("Makefile", "w").write(py_files['Makefile'].format(**format_vars))
    os.mkdir(module)
    open(os.path.join(module, module + ".py"), "w").write(py_files['module/module.py'].format(**format_vars))
    open(os.path.join(module, "__init__.py"), "w").write(py_files['module/__init__.py'])
    os.mkdir("documentation")
    open("documentation/Makefile", "w").write(py_files['documentation/Makefile'])
    open("documentation/index.html", "w").write(py_files['documentation/index.html'])
    open("documentation/config.cfg", "w").write(py_files['documentation/config.cfg'].format(**format_vars))
    open("documentation/manual.src", "w").write(py_files['documentation/manual.src'].format(**format_vars))
    open(".gitignore", "w").write(py_files['.gitignore'])


def make_files_tools(module):
    ''' Creates the files necessary for a tools module '''
    open("build", "w").write(tools_files['build'].format(**locals()))
    print("\nPlease add your patch files to the {module:s} directory and edit "
        "{module:s}/build script appropriately".format(**locals()))
    # Include .gitignore file for tools module?


def make_files_support_ioc(module):
    ''' Creates the files necessary for a support or ioc module '''
    open(".gitignore", "w").write(support_ioc_files['.gitignore'])


def set_module_contact(module_path):
    """ Adds given contact name to module """
    pass


def import_module(disk_dir, dest, args, module):
    print("Importing " + disk_dir + " into " + dest)

    svn.import_(disk_dir, dest, 'Initial structure of new ' + disk_dir, recurse=True)
    shutil.rmtree(disk_dir)

    print('Checkout ' + disk_dir + ' from ' + dest)
    svn.checkout(dest, disk_dir)
    user = os.getlogin()
    if args.area == "python":
        svn.propset("svn:ignore", "dist\nbuild\ninstalled.files\n", disk_dir)
    elif args.area in ("support", "ioc"):
        svn.propset("svn:ignore", "bin\ndata\ndb\ndbd\ninclude\nlib\n", disk_dir)
    svn.propset("dls:contact", user, disk_dir)
    svn.checkin(disk_dir, module + ": changed contact and set svn:ignore")


def main():

    parser = make_parser()
    args = parser.parse_args()

#    if len(args) != 1:
#        parser.error("Incorrect number of arguments.")

    # setup the environment
    module = args.module_name
    disk_dir = module
    app_name = module
    cwd = os.getcwd()
    from dls_environment.svn import svnClient
    svn = svnClient()

    # Check we know what to do
    if args.area not in ("ioc", "support", "tools", "python"):
        raise TypeError("Don't know how to make a module of type " + args.area)

    # setup area
    if args.area == "ioc":
        area = "ioc"    # Not used!
        cols = module.split('/')
        if len(cols) > 1 and cols[1] != '':
            domain = cols[0]
            technical_area = cols[1]
            if len(cols) == 3 and cols[2] != '':
                ioc_number = cols[2]
            else:
                ioc_number = '01'
            module = domain + "/" + technical_area
            if technical_area == "BL":
                app_name = domain
            else:
                app_name = domain + '-' + technical_area + '-' + 'IOC' + '-' + ioc_number
                if args.fullname:
                    module = domain + "/" + app_name
        else:
            # assume full IOC name is given
            cols = module.split('-')
            assert len(cols) > 1, "Need a name with dashes in it, got " + module
            domain = cols[0]
            technical_area = cols[1]
            app_name = module
            module = domain + "/" + app_name
        disk_dir = module
        # write the message for ioc BL
        BL_message = "\nPlease now edit " + \
                     os.path.join(disk_dir, "/configure/RELEASE") + \
                     " and path to scripts."
        BL_message += "\nAlso edit " + \
                      os.path.join(disk_dir, app_name + "App/src/Makefile") + \
                      " to add all database files from these technical areas."
        BL_message += "\nAn example set of screens has been placed in " + \
                      os.path.join(disk_dir, app_name + "App/opi/edl") + \
                      " . Please modify these.\n"
    elif args.area == "python":
        assert module.startswith("dls_") and "-" not in module and "." not in module,\
            "Python module names must start with 'dls_' and be valid python identifiers"

    # Remote repo check
    dest = pathf.devModule(module, args.area)

    if not args.no_import:
        dir_list = [dest, pathf.vendorModule(module, args.area),
                    pathf.prodModule(module, args.area)]
        if args.area == "ioc":
            dir_list = [x + "/" + app_name + "App" for x in dir_list]
        for dir in dir_list:
            assert not svn.pathcheck(dir), "The path " + dir + \
                                           " already exists in subversion, cannot continue"

    # Local repo check
    assert not svn.workingCopy(), \
        "Currently in a svn working copy, please move elsewhere and try again"
    assert not os.path.isdir(disk_dir), \
        "Directory ./" + disk_dir + \
        " already exists, please move elsewhere and try again"
    print("Making clean directory structure for " + disk_dir)

    os.makedirs(disk_dir)
    os.chdir(disk_dir)

    # message generation
    # Only needed in ioc if not BL module
    
    # write the message for ioc and support modules
    def_message = '\nPlease now edit ' + os.path.join(disk_dir, '/configure/RELEASE') + \
                  " to put in correct paths for dependencies."
    def_message += '\nYou can also add dependencies to ' + \
                   os.path.join(disk_dir, app_name+'App/src/Makefile')
    def_message += '\nand '+os.path.join(disk_dir, app_name + 'App/Db/Makefile') + \
                   " if appropriate."
    # write the message to python modules
    py_message = "\nPlease add your python files to the " + \
                 os.path.join(disk_dir, module) + " directory and edit " + \
                 os.path.join(disk_dir, "setup.py") + " appropriately."

    # make the module in .
    if args.area in ["ioc", "support"]:
        if args.area == "ioc":
            if technical_area == "BL":
                os.system('makeBaseApp.pl -t dlsBL ' + app_name)
                print(BL_message)
            else:
                os.system('makeBaseApp.pl -t dls ' + app_name)
                os.system('makeBaseApp.pl -i -t dls ' + app_name)
                shutil.rmtree(os.path.join(app_name+'App', 'opi'))
                print(def_message)
        else:
            os.system('makeBaseApp.pl -t dls ' + module)
            os.system('dls-make-etc-dir.py && make clean uninstall')
            print(def_message)

        # TODO make_files_support_ioc(module)  # Adds .gitignore files

    elif args.area == "tools":
        make_files_tools(module)

    elif args.area == "python":
        make_files_python(module)
        print(py_message)

    # TODO First need to stage and commit files to local repository

    if not args.no_import:
        # import the module into svn
        os.chdir(cwd)
        import_module(disk_dir, dest, args, module)

        # TODO Add remote origin and push repo


if __name__ == "__main__":
    #sys.exit(main())
    sys.exit()  # Stops us from running incomplete version!
