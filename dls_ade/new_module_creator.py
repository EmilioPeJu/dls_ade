import os
import re
import path_functions as pathf
from new_module_templates import py_files, tools_files, default_files
import vcs_git


def get_new_module_creator(args):
    ''' Use arguments to determine which new module creator to use, and return it '''

    module_name = args.module_name
    area = args.area
    cwd = os.getcwd()

    if area == "ioc":

        cols = re.split(r'[-/]+', module_name) # Similar to s.split() but works with multiple characters ('-' and '/')

        if len(cols) > 1 and cols[1] != '':
            if cols[1] == "BL":
                return NewModuleCreatorIOCBL(module_name, area, cwd)  # BL GUI module
        else:
            return NewModuleCreatorIOC(module_name, area, cwd)

    elif area == "python":
        return NewModuleCreatorPython(module_name, area, cwd)

    elif area == "support":
        return NewModuleCreatorSupport(module_name, area, cwd)

    elif area == "tools":
        return NewModuleCreatorTools(module_name, area, cwd)
    else:
        raise Exception("Don't know how to make a module of type: " + area)


def obtain_template_files(area):
    # function to generate file templates for the classes. In future will obtain from new_module_templates or file tree
    if area in ["default", "ioc", "support"]:
        return default_files
    elif area == "python":
        return py_files
    elif area == "tools":
        return tools_files
    else:
        return {}


class NewModuleCreator(object):

    def __init__(self, module_name, area, cwd):
        # Initialise all private variables, including:

        # template list - include variable list for .format()?

        # module name
        # area
        # disk directory - directory where module to be imported is located
        # app name
        # dest - location of file on server

        # Sensible defaults for variable initialisation:

        self.area = area  # needed for file templates and dest
        self.module_name = module_name
        self.cwd = cwd
        self.disk_dir = self.module_name
        self.app_name = self.module_name
        self.dest = pathf.devModule(self.module_name, self.area)

        self.message = ""
        self.compose_message()

        self.template_files = {}
        self.generate_template_files()
        self.template_args = {}
        self.generate_template_args()

        self.remote_repo_valid = False   # check_remote_repo must be called in order to export module files
        self.local_repo_valid = False    # check_local_repo must be called before creating files
        self.local_repo_created = False  # local repo must have been created before

    def compose_message(self):
        ''' Generates the message to print out to the user on creation of the module files '''

        message_dict = {'RELEASE':os.path.join(self.disk_dir, '/configure/RELEASE'),
                        'srcMakefile': os.path.join(self.disk_dir, self.app_name + 'App/src/Makefile'),
                        'DbMakefile': os.path.join(self.disk_dir, self.app_name + 'App/Db/Makefile')}

        message = "\nPlease now edit {RELEASE:s} to put in correct paths for dependencies."
        message += "\nYou can also add dependencies to {srcMakefile:s}"
        message += "\nand {DbMakefile:s} if appropriate."
        message = message.format(**message_dict)

        self.message = message

    def generate_template_files(self):
        ''' Generates the template files dictionary that can be used to create default module files '''
        self.template_files = obtain_template_files(self.area)

    def check_remote_repo(self):
        # Creates and uses dir_list to check remote repository for name collisions with new module - part of init?

        dir_list = self.get_remote_dir_list()

        valid = True

        for d in dir_list:
            if vcs_git.is_repo_path(d):
                valid = False
                break

        self.remote_repo_valid = valid

    def get_remote_dir_list(self):
        dest = self.dest
        vendor_path = pathf.vendorModule(self.module_name, self.area)
        prod_path = pathf.prodModule(self.module_name, self.area)

        return [dest, vendor_path, prod_path]

    def check_local_repo(self):
        # Checks that 'we' are not currently in a git repository, and that there are no name conflictions for the files
        # to be created

        raise NotImplementedError

    def generate_template_args(self):
        ''' returns a dictionary that can be used for the .format method, used in creating files '''
        template_args = {'module': self.module_name, 'getlogin': os.getlogin()}

        self.template_args = template_args

    def create_files(self):
        # Creates the files (possibly in subdirectories) as part of the module creation process
        # Part of this involves chdir into the module directory, and exiting at the end of the process
        # Uses makeBaseApp, dls-etc-dir.py and make_files functions depending on area of module

        # Likely abstract, as all classes behave slightly differently

        # Need to print:     print("Making clean directory structure for " + disk_dir)
        # Need to check local_repo_valid first
        # Set local_repo_valid false after running
        raise NotImplementedError

    def add_contact(self):
        # Add the module contact to the contacts database
        raise NotImplementedError

    def print_messages(self):
        # Prints the messages previously constructed. Could move message creation after file generation
        # Move the print statement from make_files_tools to here!

        print(self.message)

    def stage_and_commit(self):
        # Stages and commits the files to the local repository. Separate from export repo as export not always done!
        # Switch statement in export?

        # Need ... to be false
        raise NotImplementedError

    def push_repo_to_remote(self):
        # Pushes the local repo to the remote server.

        # Need ... to be true / false
        raise NotImplementedError


class NewModuleCreatorIOC(NewModuleCreator):

    def __init__(self, module, area, cwd, technical_area):
        super(NewModuleCreatorIOC, self).__init__(self, module, area, cwd)
        # Initialise all private variables, including:
            # template list - include variable list for .format()?
            # module name
            # area
            # disk directory - directory where module to be imported is located
            # app name
            # dest - location of file on server

        raise NotImplementedError

    pass


class NewModuleCreatorIOCBL(NewModuleCreator):
    pass


class NewModuleCreatorPython(NewModuleCreator):
    pass


class NewModuleCreatorSupport(NewModuleCreator):
    pass


class NewModuleCreatorTools(NewModuleCreator):
    pass
