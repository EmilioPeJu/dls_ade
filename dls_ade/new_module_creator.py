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

        self.remote_repo_valid = False   # check_remote_repo_valid must be called in order to export module files
        self.local_dir_valid = False     # check_local_dir_valid must be called before creating files
        self.local_repo_created = False  # local repo must not be created before init and commit; must be before push

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

    def generate_template_args(self):
        ''' returns a dictionary that can be used for the .format method, used in creating files '''
        template_args = {'module': self.module_name, 'getlogin': os.getlogin()}

        self.template_args = template_args

    def check_remote_repo_valid(self):
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

    def check_local_dir_valid(self):
        ''' Determines whether the local directory is a valid starting point for module file structure creation '''
        # Checks that 'we' are not currently in a git repository, and that there are no name conflicts for the files
        # to be created

        mod_dir_exists = os.path.isdir(self.disk_dir)  # move to function where creation takes place?

        if mod_dir_exists:
            fail_message = "Directory ./{dd:s} already exists,"
            fail_message += " please move elsewhere and try again"
            print(fail_message.format(dd=self.disk_dir))
            return False

        cwd_is_repo = vcs_git.is_git_dir()  # true if currently inside git repository
                                            # NOTE: Does not detect if further folder is git repo - how to fix?
        if cwd_is_repo:
            fail_message = "Currently in a git repository, please move elsewhere and try again"
            print(fail_message)
            return False

        return True

    def check_local_repo_created(self):
        ''' Determines whether or not the module directory is now a git repo, ready for exporting ('git push') '''

        mod_dir_is_repo = vcs_git.is_git_root_dir(self.disk_dir)

        if not mod_dir_is_repo:
            fail_message = "Directory ./{dd:s} is not currently a git repository,"
            fail_message += "so the module cannot be exported"
            print(fail_message.format(dd=self.disk_dir))
            return False

        return True

    # def create_module(self):
    #     ''' General function that controls the creation of files and folders in a new module. Same for all classes '''
    #     # cd's into module directory, and creates complete file hierarchy before exiting
    #
    #     if not self.check_local_dir_valid():
    #         self.check_local_dir_valid()
    #         if self.local_dir_valid is False:
    #             raise Exception("Module cannot be created as local directory is not valid")
    #     else:
    #         print("Making clean directory structure for " + self.disk_dir)
    #         os.chdir(os.path.join(self.cwd,self.disk_dir))
    #         self.create_files()
    #         os.chdir(self.cwd)

    # def create_files(self):
    #     # Uses makeBaseApp, dls-etc-dir.py and make_files functions depending on area of module
    #     # Default just sticks to template dictionary entries
    #
    #     # All classes behave slightly differently
    #
    #     # self.add_contact() # If contacts exist in the repository, they ought to be added here (or added to dict)
    #     self.recursively_create_files()

    # def recursively_create_files(self):
    #     ''' Iterates through the template dict and creates all necessary files and folders '''
    #
    #     for rel_path in self.template_files:  # dictionary keys are the relative file paths for the documents
    #         abs_dir = os.path.dirname(os.path.abspath(rel_path))
    #         if not os.isdir(abs_dir):
    #             os.makedirs(abs_dir)
    #
    #         open(rel_path, "w").write(self.template_files[rel_path].format(**self.template_args))

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
