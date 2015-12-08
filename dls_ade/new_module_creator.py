from __future__ import print_function
import os
import re
import path_functions as pathf
import shutil
from new_module_templates import py_files, tools_files, default_files
import vcs_git


def get_new_module_creator(module_name, area="support", fullname=False):
    ''' Use arguments to determine which new module creator to use, and return it '''

    cwd = os.getcwd()

    if area == "ioc":  # This section of code is ugly because it has to mimic the behaviour of the original script
        cols = module_name.split('/')  # Feel free to modify if you think you can tidy it up a bit! (use unit tests)
        if len(cols) > 1 and cols[1] != '':
            domain = cols[0]
            technical_area = cols[1]

            if technical_area == "BL":
                module_path = domain + "/" + technical_area
                app_name = domain
                return NewModuleCreatorIOCBL(module_path, app_name, area, cwd)

            if len(cols) == 3 and cols[2] != '':
                ioc_number = cols[2]
            else:
                ioc_number = '01'

            app_name = domain + '-' + technical_area + '-' + 'IOC' + '-' + ioc_number
            if fullname:
                module_path = domain + "/" + app_name
                return NewModuleCreatorIOC(module_path, app_name, area, cwd)
            else:
                module_path = domain + "/" + technical_area
                return NewModuleCreatorIOCOldNaming(module_path, app_name, area, cwd)
        else:
            # assume full IOC name is given
            cols = module_name.split('-')
            if len(cols) <= 1:
                raise Exception("Need a name with dashes in it, got " + module_name)
            domain = cols[0]
            technical_area = cols[1]
            app_name = module_name
            module_path = domain + "/" + app_name

            if technical_area == "BL":
                return NewModuleCreatorIOCBL(module_path, app_name, area, cwd)
            else:
                return NewModuleCreatorIOC(module_path, app_name, area, cwd)

    elif area == "python":
        valid_name = module_name.startswith("dls_") and ("-" not in module_name) and ("." not in module_name)
        if not valid_name:
            raise Exception("Python module names must start with 'dls_' and be valid python identifiers")

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

    def __init__(self, module_path, area, cwd):
        # Initialise all private variables.
        # This one is used for testing purposes, although it is also used by support, tools and python

        # template list - include variable list for .format()?

        # module name
        # area
        # disk directory - directory where module to be imported is located
        # app name
        # dest - location of file on server

        # Sensible defaults for variable initialisation:

        self.area = area  # needed for file templates and dest
        self.cwd = cwd

        self.module_path = ""
        self.module_name = ""
        self.app_name = ""
        self.module_path = module_path  # module_path has module_name at end, and folder is to contain "<app_name>App"

        self.module_name = os.path.basename(os.path.normpath(self.module_path))  # Last part of module_path
        self.app_name = self.module_name

        # The above declarations could be separated out into a new function, which may then be altered by new classes

        self.disk_dir = ""
        self.disk_dir = self.module_path
        self.dest = pathf.devModule(self.module_path, self.area)

        self.message = ""
        # self.compose_message()

        self.template_files = {}
        self.generate_template_files()
        self.template_args = {}
        self.generate_template_args()

        # This flag determines whether there are conflicting file names on the remote repository
        self.remote_repo_valid = False  # call function at start
        # These flags must be true before the corresponding function can be called
        self.create_module_valid = False  # call function at start
        # self.create_local_repo_valid = False
        self.push_repo_to_remote_valid = False
        # This set of 'valid' flags allows us to call the member functions in whatever order we like, and receive
        # appropriate error messages

    def compose_message(self):
        ''' Generates the message to print out to the user on creation of the module files '''

        message_dict = {'RELEASE': os.path.join(self.disk_dir, '/configure/RELEASE'),
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
        ''' returns a dictionary that can be used for the .format() method, used in creating files '''
        template_args = {'module': self.module_path, 'getlogin': os.getlogin()}

        self.template_args = template_args

    def check_remote_repo_valid(self):
        # Creates and uses dir_list to check remote repository for name collisions with new module - part of init?

        dir_list = self.get_remote_dir_list()
        return_message = ""

        valid = True

        for d in dir_list:
            if vcs_git.is_repo_path(d):
                valid = False
                return_message = "The path {dir:s} already exists in subversion, cannot continue".format(dir=d)
                break

        self.remote_repo_valid = valid
        return valid, return_message

    def get_remote_dir_list(self):
        dest = self.dest
        vendor_path = pathf.vendorModule(self.module_path, self.area)
        prod_path = pathf.prodModule(self.module_path, self.area)

        dir_list = [dest, vendor_path, prod_path]

        return dir_list

    def check_create_module_valid(self):
        ''' Determines whether the local directory is a valid starting point for module file structure creation '''
        # Checks that 'we' are not currently in a git repository, and that there are no name conflicts for the files
        # to be created

        return_message = ""
        valid = True

        mod_dir_exists = os.path.isdir(self.disk_dir)  # move to function where creation takes place?
        cwd_is_repo = vcs_git.is_git_dir()  # true if currently inside git repository
                                            # NOTE: Does not detect if further folder is git repo - how to fix?

        if mod_dir_exists and cwd_is_repo:
            return_message = "Directory {dir:s} already exists AND currently in a git repository."
            return_message += " Please move elsewhere and try again"
            valid = False
        elif mod_dir_exists:
            return_message = "Directory {dir:s} already exists, please move elsewhere and try again"
            valid = False
        elif cwd_is_repo:
            return_message = "Currently in a git repository, please move elsewhere and try again"
            valid = False

        return_message = return_message.format(dir=os.path.join("./", self.disk_dir))
        self.create_module_valid = valid
        return valid, return_message

    # def check_create_local_repo_valid(self):
    #     ''' Determines whether the local directory is valid for creating and committing a new git repository '''
    #     # Checks that the folder exists and is not currently inside a git repository
    #
    #     return_message = ""
    #     valid = True
    #
    #     mod_dir_exists = os.path.isdir(self.disk_dir)  # move to function where creation takes place?
    #
    #     if not mod_dir_exists:
    #         return_message = "Directory {dir:s} does not exist"
    #         return_message = return_message.format(dir=os.path.join("./", self.disk_dir))
    #         valid = False
    #     else:
    #         mod_dir_is_in_repo = vcs_git.is_git_dir(self.disk_dir)  # true if folder currently inside git repository
    #         if mod_dir_is_in_repo:
    #             return_message = "Directory {dir:s} is inside git repository. Cannot initialise git repository"
    #             return_message = return_message.format(dir=os.path.join("./", self.disk_dir))
    #             valid = False
    #
    #     self.create_local_repo_valid = valid
    #     return valid, return_message

    def check_push_repo_to_remote_valid(self):
        ''' Determines whether one can push the local repository to the remote one '''
        # Checks that the folder exists, is a git repository and there are no remote server module path clashes

        return_message = ""
        valid = True

        mod_dir_exists = os.path.isdir(self.disk_dir)  # move to function where creation takes place?

        if not mod_dir_exists:
            return_message = "Directory {dir:s} does not exist"

            valid = False
        else:
            mod_dir_is_repo = vcs_git.is_git_root_dir(self.disk_dir)  # true if folder currently inside git repository
            if not mod_dir_is_repo:
                return_message = "Directory {dir:s} is not a git repository. Unable to push to remote repository"
                valid = False

        if not self.remote_repo_valid:  # Doing it this way allows us to retain the remote_repo_valid error message
            repo_valid, repo_return_message = self.check_remote_repo_valid()
            if (not repo_valid) and (not valid):
                return_message += "\nAND: " + repo_return_message
            else:
                return_message = repo_return_message
                valid = repo_valid

        return_message = return_message.format(dir=os.path.join("./", self.disk_dir))
        self.push_repo_to_remote_valid = valid
        return valid, return_message

    def create_module(self):
        ''' General function that controls the creation of files and folders in a new module. Same for all classes '''
        # cd's into module directory, and creates complete file hierarchy before exiting

        if not self.create_module_valid:
            valid, return_message = self.check_create_module_valid()
            if not valid:
                raise Exception(return_message)

        self.create_module_valid = False

        print("Making clean directory structure for " + self.disk_dir)

        if not os.path.isdir(self.disk_dir):
            os.makedirs(self.disk_dir)

        vcs_git.init_repo(self.disk_dir)

        os.chdir(os.path.join(self.cwd, self.disk_dir))
        self._create_files()
        os.chdir(self.cwd)

        # self.commit_to_local_repo()  # No longer needed
        vcs_git.stage_all_files_and_commit(self.disk_dir)

    def _create_files(self):
        # Uses makeBaseApp, dls-etc-dir.py and make_files functions depending on area of module
        # Default just sticks to template dictionary entries

        # All classes behave slightly differently

        # self.add_contact() # If contacts exist in the repository, they ought to be added here (or added to dict)
        self.create_files_from_template_dict()

    def create_files_from_template_dict(self):
        ''' Iterates through the template dict and creates all necessary files and folders '''
        # As dictionaries cannot have more than one key, and the directory does not previously exist, should I
        # error check?

        for rel_path in self.template_files:  # dictionary keys are the relative file paths for the documents
            dir_path = os.path.dirname(rel_path)

            if os.path.normpath(dir_path) == os.path.normpath(rel_path):
                # If folder given instead of file (ie. rel_path ends with a slash or folder already exists)
                raise Exception("{dir:s} in template dictionary is not a valid file name".format(dir=dir_path))
            else:
                if not os.path.isdir(dir_path):
                    os.makedirs(dir_path)

                open(rel_path, "w").write(self.template_files[rel_path].format(**self.template_args))

    def add_contact(self):
        # Add the module contact to the contacts database
        raise NotImplementedError

    def print_messages(self):
        # Prints the messages previously constructed. Could move message creation after file generation
        # Move the print statement from make_files_tools to here!

        print(self.message)

    # def commit_to_local_repo(self):
    #     # Stages and commits the files to the local repository.
    #
    #     if not self.create_local_repo_valid:
    #         valid, return_message = self.check_create_local_repo_valid()
    #         if not valid:
    #             raise Exception(return_message)
    #
    #     self.create_local_repo_valid = False
    #
    #     vcs_git.stage_all_files_and_commit(self.disk_dir)

    def push_repo_to_remote(self):
        # Pushes the local repo to the remote server.

        if not self.push_repo_to_remote_valid:
            valid, return_message = self.check_push_repo_to_remote_valid()
            if not valid:
                raise Exception(return_message)

        self.push_repo_to_remote_valid = False

        vcs_git.create_new_remote_and_push(self.area, self.module_path, self.disk_dir)


class NewModuleCreatorIOC(NewModuleCreator):

    def __initialise_and_verify_module_variables(self, args):

        # cols = args.module_name.split("/")
        # if len(cols) > 1 and cols[1] != '':
        #     domain = cols[0]
        #     technical_area = cols[1]
        #     if len(cols) == 3 and cols[2] != '':
        #         ioc_number = cols[2]
        #     else:
        #         ioc_number = '01'
        #     self.app_name = domain + '-' + technical_area + '-IOC-' + ioc_number
        #
        #     if args.fullname:
        #         self.module_name = domain + "/" + self.app_name
        #     else:
        #         self.module_name = domain + "/" + technical_area
        # else:
        #     cols = args.module_name.split("-")
        #     if len(cols) > 1:
        #         domain = cols[0]
        #         self.app_name = args.module_name
        #         self.module_name = domain + "/" + self.app_name
        #     else:  # If module_name not in correct format
        #         raise Exception("Need a name with dashes in it, got " + args.module_name)
        raise NotImplementedError

    def _create_files(self):

        # os.system('makeBaseApp.pl -t dls ' + self.app_name)
        # os.system('makeBaseApp.pl -i -t dls ' + self.app_name)
        # shutil.rmtree(os.path.join(self.app_name+'App', 'opi'))
        # print(self.message)
        # self.create_files_from_template_dict()
        raise NotImplementedError


class NewModuleCreatorIOCOldNaming(NewModuleCreatorIOC):
    # Also need:
    # check_remote_repo_valid to look inside module if it exists
    # create_module
    # create_local_repo

    def __initialise_and_verify_module_variables(self, args):

        # cols = args.module_name.split("/")
        # if len(cols) > 1 and cols[1] != '':
        #     domain = cols[0]
        #     technical_area = cols[1]
        #     if len(cols) == 3 and cols[2] != '':
        #         ioc_number = cols[2]
        #     else:
        #         ioc_number = '01'
        #     self.app_name = domain + '-' + technical_area + '-IOC-' + ioc_number
        #
        #     if args.fullname:
        #         self.module_name = domain + "/" + self.app_name
        #     else:
        #         self.module_name = domain + "/" + technical_area
        # else:
        #     cols = args.module_name.split("-")
        #     if len(cols) > 1:
        #         domain = cols[0]
        #         self.app_name = args.module_name
        #         self.module_name = domain + "/" + self.app_name
        #     else:  # If module_name not in correct format
        #         raise Exception("Need a name with dashes in it, got " + args.module_name)
        raise NotImplementedError

    def _create_files(self):

        # os.system('makeBaseApp.pl -t dls ' + self.app_name)
        # os.system('makeBaseApp.pl -i -t dls ' + self.app_name)
        # shutil.rmtree(os.path.join(self.app_name+'App', 'opi'))
        # print(self.message)
        # self.create_files_from_template_dict()
        raise NotImplementedError


class NewModuleCreatorIOCBL(NewModuleCreator):  # Note: does NOT inherit from NewModuleCreatorIOC (no shared code)
    
    def __initialise_and_verify_module_variables(self, args):

        # cols = args.module_name.split('/')
        #
        # if len(cols) > 1 and cols[1] != '':
        #     domain = cols[0]
        #     technical_area = cols[1]
        #     module = domain + "/" + technical_area
        #     app_name = domain
        # else:
        #     cols = args.module_name.split("-")
        #     if len(cols) < 2:
        #         raise Exception("Need a name with dashes in it, got " + args.module_name)
        #
        #     domain = cols[0]
        #     self.app_name = args.module_name
        #     self.module_name = domain + "/" + self.app_name
        raise NotImplementedError

    def _create_files(self):

        # os.system('makeBaseApp.pl -t dlsBL ' + app_name)
        # self.create_files_from_template_dict()
        raise NotImplementedError

    def compose_message(self):

        # message_dict = {'RELEASE': os.path.join(self.disk_dir, '/configure/RELEASE'),
        #     'srcMakefile': os.path.join(self.disk_dir, self.app_name + 'App/src/Makefile'),
        #     'DbMakefile': os.path.join(self.disk_dir, self.app_name + 'App/Db/Makefile')}
        # message = "\nPlease now edit {RELEASE:s} and path to scripts."
        # message += "\nAlso edit {srcMakefile:s} to add all database files from these technical areas."
        # message += "\nAn example set of screens has been placed in {DbMakefile:s} . Please modify these.\n"
        #
        # message = message.format(**message_dict)
        #
        # self.message = message
        raise NotImplementedError


class NewModuleCreatorPython(NewModuleCreator):
    
    def __initialise_and_verify_module_variables(self, args):

        # module_name = args.module_name
        #
        # if not module_name.startswith("dls_") and "-" not in module_name and "." not in module_name:
        #     raise Exception("Python module names must start with 'dls_' and be valid python identifiers")
        # self.module_name = args.module_name
        # self.app_name = self.module_name
        raise NotImplementedError

    def compose_message(self):

        # message_dict = {'module_path': os.path.join(self.disk_dir, self.module_path),
        #                 'setup_path': os.path.join(self.disk_dir, "setup.py")}
        #
        # message = "\nPlease add your python files to the {module_path:s} directory"
        # message += " and edit {setup_path} appropriately."
        #
        # message = message.format(message_dict)
        #
        # self.message = message
        raise NotImplementedError


class NewModuleCreatorSupport(NewModuleCreator):
    
    def _create_files(self):

        # os.system('makeBaseApp.pl -t dls ' + self.module_path)
        # os.system('dls-make-etc-dir.py && make clean uninstall')
        # self.create_files_from_template_dict()
        raise NotImplementedError


class NewModuleCreatorTools(NewModuleCreator):
    
    def compose_message(self):

        # message_dict = {"module": self.module_path}
        #
        # message = "\nPlease add your patch files to the {module:s} directory"
        # message += " and edit {module:s}/build script appropriately"
        #
        # message = message.format(message_dict)
        # self.message = message
        raise NotImplementedError
