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
        if len(cols) > 1 and cols[1] == "BL":
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
        self.cwd = cwd

        # self.module_name = module_name
        # self.disk_dir = self.module_name
        # self.app_name = self.module_name
        # The above declarations could be separated out into a new function, which may then be altered by new classes

        self.module_name = ""
        self.disk_dir = ""
        self.app_name = ""
        self.__initialise_and_verify_module_variables(module_name, area)
        # The above declarations could be separated out into a new function, which may then be altered by new classes

        self.dest = pathf.devModule(self.module_name, self.area)

        self.message = ""
        self.compose_message()

        self.template_files = {}
        self.generate_template_files()
        self.template_args = {}
        self.generate_template_args()

        # This flag determines whether there are conflicting file names on the remote repository
        self.remote_repo_valid = False  # call function at start
        # These flags must be true before the corresponding function can be called
        self.create_module_valid = False  # call function at start
        self.init_stage_and_commit_valid = False
        self.push_repo_to_remote_valid = False
        # This set of 'valid' flags allows us to call the member functions in whatever order we like, and receive
        # appropriate error messages

    def __initialise_and_verify_module_variables(self, module_name, area):
        ''' initialisation and verification of module_name, disk_dir and app_name '''
        # Default is straightforward, but this is more complex for IOC (BL) modules (Python also has verification)

        self.module_name = module_name
        self.disk_dir = self.module_name
        self.app_name = self.module_name
        pass

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
        ''' returns a dictionary that can be used for the .format() method, used in creating files '''
        template_args = {'module': self.module_name, 'getlogin': os.getlogin()}

        self.template_args = template_args

    def check_remote_repo_valid(self):
        # Creates and uses dir_list to check remote repository for name collisions with new module - part of init?

        dir_list = self.get_remote_dir_list()
        err_message = ""

        valid = True

        for d in dir_list:
            if vcs_git.is_repo_path(d):
                valid = False
                err_message = "The path {dir:s} already exists in subversion, cannot continue".format(dir=d)
                break

        self.remote_repo_valid = valid
        return valid, err_message

    def get_remote_dir_list(self):
        dest = self.dest
        vendor_path = pathf.vendorModule(self.module_name, self.area)
        prod_path = pathf.prodModule(self.module_name, self.area)

        dir_list = [dest, vendor_path, prod_path]

        return dir_list

    def check_create_module_valid(self):
        ''' Determines whether the local directory is a valid starting point for module file structure creation '''
        # Checks that 'we' are not currently in a git repository, and that there are no name conflicts for the files
        # to be created

        err_message = ""
        valid = True

        mod_dir_exists = os.path.isdir(self.disk_dir)  # move to function where creation takes place?
        cwd_is_repo = vcs_git.is_git_dir()  # true if currently inside git repository
                                            # NOTE: Does not detect if further folder is git repo - how to fix?

        if mod_dir_exists and cwd_is_repo:
            err_message = "Directory {dir:s} already exists AND currently in a git repository."
            err_message += " Please move elsewhere and try again"
            valid = False
        elif mod_dir_exists:
            err_message = "Directory {dir:s} already exists, please move elsewhere and try again"
            valid = False
        elif cwd_is_repo:
            err_message = "Currently in a git repository, please move elsewhere and try again"
            valid = False

        err_message = err_message.format(dir=os.path.join("./", self.disk_dir))
        self.create_module_valid = valid
        return valid, err_message

    def check_init_stage_and_commit_valid(self):
        ''' Determines whether the local directory is valid for creating and committing a new git repository '''
        # Checks that the folder exists and is not currently inside a git repository

        err_message = ""
        valid = True

        mod_dir_exists = os.path.isdir(self.disk_dir)  # move to function where creation takes place?

        if not mod_dir_exists:
            err_message = "Directory {dir:s} does not exist"
            err_message = err_message.format(dir=os.path.join("./", self.disk_dir))
            valid = False
        else:
            mod_dir_is_in_repo = vcs_git.is_git_dir(self.disk_dir)  # true if folder currently inside git repository
            if mod_dir_is_in_repo:
                err_message = "Directory {dir:s} is inside git repository. Cannot initialise git repository"
                err_message = err_message.format(dir=os.path.join("./", self.disk_dir))
                valid = False

        self.init_stage_and_commit_valid = valid
        return valid, err_message

    def check_push_repo_to_remote_valid(self):
        ''' Determines whether one can push the local repository to the remote one '''
        # Checks that the folder exists, is a git repository and there are no remote server module path clashes

        # err_message = ""
        # valid = True
        #
        # mod_dir_exists = os.path.isdir(self.disk_dir)  # move to function where creation takes place?
        #
        # if not mod_dir_exists:
        #     err_message = "Directory {dir:s} does not exist"
        #     err_message = err_message.format(dir=os.path.join("./", self.disk_dir))
        #     valid = False
        # else:
        #     mod_dir_is_repo = vcs_git.is_git_root_dir(self.disk_dir)  # true if folder currently inside git repository
        #     if not mod_dir_is_repo:
        #         err_message = "Directory {dir:s} is not git repository. Unable to push to remote repository"
        #         err_message = err_message.format(dir=os.path.join("./", self.disk_dir))
        #         valid = False
        #     elif not self.remote_repo_valid:
        #         valid, err_message = self.check_remote_repo_valid()
        #
        # self.push_repo_to_remote_valid = valid
        # return valid, err_message

        err_message = ""
        valid = True

        mod_dir_exists = os.path.isdir(self.disk_dir)  # move to function where creation takes place?

        if not mod_dir_exists:
            err_message = "Directory {dir:s} does not exist"

            valid = False
        else:
            mod_dir_is_repo = vcs_git.is_git_root_dir(self.disk_dir)  # true if folder currently inside git repository
            if not mod_dir_is_repo:
                err_message = "Directory {dir:s} is not a git repository. Unable to push to remote repository"
                valid = False

        if not self.remote_repo_valid:  # Doing it this way allows us to retain the remote_repo_valid error message
            repo_valid, repo_err_message = self.check_remote_repo_valid()
            if (not repo_valid) and (not valid):
                err_message += "\nAND: " + repo_err_message
            else:
                err_message = repo_err_message
                valid = repo_valid

        err_message = err_message.format(dir=os.path.join("./", self.disk_dir))
        self.push_repo_to_remote_valid = valid
        return valid, err_message

    def create_module(self):
        ''' General function that controls the creation of files and folders in a new module. Same for all classes '''
        # cd's into module directory, and creates complete file hierarchy before exiting

        if not self.create_module_valid:
            valid, err_message = self.check_create_module_valid()
            if not valid:
                raise Exception(err_message)
        else:
            print("Making clean directory structure for " + self.disk_dir)
            os.chdir(os.path.join(self.cwd, self.disk_dir))
            self.create_files()
            os.chdir(self.cwd)

    def create_files(self):
        # Uses makeBaseApp, dls-etc-dir.py and make_files functions depending on area of module
        # Default just sticks to template dictionary entries

        # All classes behave slightly differently

        # self.add_contact() # If contacts exist in the repository, they ought to be added here (or added to dict)
        self.create_files_from_template_dict()

    def create_files_from_template_dict(self):
        ''' Iterates through the template dict and creates all necessary files and folders '''

        for rel_path in self.template_files:  # dictionary keys are the relative file paths for the documents
            abs_dir = os.path.dirname(os.path.abspath(rel_path))
            if not os.path.isdir(abs_dir):
                os.makedirs(abs_dir)

            open(rel_path, "w").write(self.template_files[rel_path].format(**self.template_args))

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

    def __init__(self, module_name, cwd):
        super(NewModuleCreatorIOC, self).__init__(self, area)
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
