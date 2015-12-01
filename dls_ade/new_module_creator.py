import os
import re
import path_functions as pathf
from new_module_templates import py_files, tools_files, default_files


def get_new_module_creator(args):
    ''' Use arguments to determine which new module creator to use, and return it '''

    module_name = args.module_name
    area = args.area
    no_import = args.no_import
    cwd = os.getcwd()

    if area == "ioc":

        cols = re.split(r'[-/]+', module_name) # Similar to s.split() but works with multiple characters ('-' and '/')

        if len(cols) > 1 and cols[1] != '':
            if cols[1] == "BL":
                return NewModuleCreatorIOCBL(module_name, area, cwd, args.no_import)  # BL GUI module
        else:
            return NewModuleCreatorIOC(module_name, area, cwd, args.no_import)

    elif area == "python":
        return NewModuleCreatorPython(module_name, area, cwd, args.no_import)

    elif area == "support":
        return NewModuleCreatorSupport(module_name, area, cwd, args.no_import)

    elif area == "tools":
        return NewModuleCreatorTools(module_name, area, cwd, args.no_import)
    else:
        raise Exception("Don't know how to make a module of type: " + area)


def generate_template_files(area):
    # function to generate file templates for the classes. In future will obtain from new_module_templates or file tree
    if area in ["default", "ioc", "support"]:
        return default_files
    elif area == "python":
        return py_files
    elif area == "tools":
        return tools_files
    else:
        return {}


class NewModuleCreator:

    def __init__(self, module_name, area, cwd, no_import = False):
        # Initialise all private variables, including:

        # template list - include variable list for .format()?

        # module name
        # area
        # disk directory - directory where module to be imported is located
        # app name
        # dest - location of file on server

        # Sensible defaults for variable initialisation:

        self.__no_import = no_import
        self.__area = area  # needed for file templates and dest
        self.__module_name = module_name
        self.__cwd = cwd
        self.__disk_dir = self.__module_name
        self.__app_name = self.__module_name
        self.__dest = pathf.devModule(self.__module_name, self.__area)

        self.__message = self.compose_message()

        self.__template_files = generate_template_files(self.__area)
        self.__template_args = self.generate_template_args()


        #self.check_remote_repo()
        #self.check_local_repo()

        # raise NotImplementedError

    def compose_message(self):
        ''' Generates the message to print out to the user on creation of the module files '''

        message_dict = {'RELEASE':os.path.join(self.__disk_dir, '/configure/RELEASE'),
                        'srcMakefile': os.path.join(self.__disk_dir, self.__app_name+'App/src/Makefile'),
                        'DbMakefile': os.path.join(self.__disk_dir, self.__app_name + 'App/Db/Makefile')}

        message = "\nPlease now edit {RELEASE:s} to put in correct paths for dependencies."
        message += "\nYou can also add dependencies to {srcMakefile:s}\nand {DbMakefile:s} if appropriate."

        return message

    def check_remote_repo(self):
        # Creates and uses dir_list to check remote repository for name collisions with new module - part of init?
        raise NotImplementedError

    def check_local_repo(self):
        # Checks that 'we' are not currently in a git repository, and that there are no name conflictions for the files
        # to be created
        raise NotImplementedError

    def generate_template_args(self):
        ''' returns a dictionary that can be used for the .format method, used in creating files '''
        template_args = {'module': self.__module_name, 'getlogin': os.getlogin()}

        return template_args

    def create_files(self):
        # Creates the files (possibly in subdirectories) as part of the module creation process
        # Part of this involves chdir into the module directory, and exiting at the end of the process
        # Uses makeBaseApp, dls-etc-dir.py and make_files functions depending on area of module

        # Likely abstract, as all classes behave slightly differently
        raise NotImplementedError

    def add_contact(self):
        # Add the module contact to the contacts database
        raise NotImplementedError

    def print_messages(self):
        # Prints the messages previously constructed. Could move message creation after file generation
        # Move the print statement from make_files_tools to here!
        raise NotImplementedError

    def stage_and_commit(self):
        # Stages and commits the files to the local repository. Separate from export repo as export not always done!
        # Switch statement in export?
        raise NotImplementedError

    def push_repo_to_remote(self):
        # Pushes the local repo to the remote server.
        raise NotImplementedError

    @property
    def cwd(self):
        return self.__cwd


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
