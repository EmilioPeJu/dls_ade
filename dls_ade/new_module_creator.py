from __future__ import print_function
import os
import path_functions as pathf
import shutil
import tempfile
from new_module_templates import py_files, tools_files, default_files
import vcs_git


def get_new_module_creator(module_name, area="support", fullname=False):
    ''' Use arguments to determine which new module creator to use, and return it '''

    if area == "ioc":  # This section of code is ugly because it has to mimic the behaviour of the original script
        cols = module_name.split('/')  # Feel free to modify if you think you can tidy it up a bit! (use unit tests)
        if len(cols) > 1 and cols[1] != '':
            domain = cols[0]
            technical_area = cols[1]

            if technical_area == "BL":
                module_path = domain + "/" + technical_area
                app_name = domain
                return NewModuleCreatorIOCBL(module_path, app_name, area)

            if len(cols) == 3 and cols[2] != '':
                ioc_number = cols[2]

            else:
                ioc_number = '01'

            app_name = domain + '-' + technical_area + '-' + 'IOC' + '-' + ioc_number

            if fullname:
                module_path = domain + "/" + app_name
                return NewModuleCreatorIOC(module_path, app_name, area)

            else:
                module_path = domain + "/" + technical_area
                # This part is here to retain compatibility with "old-style" modules, in which a single module named
                # "domain/technical_area" contains multiple domain-technical_area-IOC-xxApp's. This involves cloning
                # from the remote repository, a different method for checking whether or not the App will conflict with
                # one on the server and not having to "git remote add origin" to the local repository. I have therefore
                # moved this code into a separate class. However, if the module does not previously exist, the process
                # is exactly the same as that described by NewModuleCreatorIOC.
                server_repo_path = pathf.devModule(module_path, area)
                if vcs_git.is_repo_path(server_repo_path):
                    # Adding new App to old style "domain/tech_area" module that already exists on the remote server
                    return NewModuleCreatorIOCAddToModule(module_path, app_name, area)

                else:
                    # Otherwise, the behaviour is exactly the same as that given by the ordinary IOC class
                    # as module_path is the only thing that varies
                    return NewModuleCreatorIOC(module_path, app_name, area)

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
                return NewModuleCreatorIOCBL(module_path, app_name, area)
            else:
                return NewModuleCreatorIOC(module_path, app_name, area)

    elif area == "python":
        valid_name = module_name.startswith("dls_") and ("-" not in module_name) and ("." not in module_name)
        if not valid_name:
            raise Exception("Python module names must start with 'dls_' and be valid python identifiers")

        return NewModuleCreatorPython(module_name, area)

    elif area == "support":
        return NewModuleCreatorSupport(module_name, area)

    elif area == "tools":
        return NewModuleCreatorTools(module_name, area)

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


class VerificationError(Exception):  # To allow us to handle and concatenate internal verification errors only
    pass


class NewModuleCreator(object):

    def __init__(self, module_path, area):
        # Initialise all private variables.
        # This one is used for testing purposes, although it is also used by support, tools and python

        # template list - include variable list for .format()?

        # module name
        # area
        # disk directory - directory where module to be imported is located
        # app name
        # server_repo_path - location of file on server

        # Sensible defaults for variable initialisation:

        self.area = area  # needed for file templates and server_repo_path
        self.cwd = os.getcwd()  # Should I be passing this as a parameter? - doing this makes the change easy!

        self.module_path = ""
        self.module_name = ""
        self.module_path = module_path  # module_path has module_name at end, and folder is to contain "<app_name>App"
        self.module_name = os.path.basename(os.path.normpath(self.module_path))  # Last part of module_path

        # The above declarations could be separated out into a new function, which may then be altered by new classes

        self.disk_dir = ""
        self.server_repo_path = ""
        self.disk_dir = os.path.join(self.cwd, self.module_path)
        self.server_repo_path = pathf.devModule(self.module_path, self.area)

        self.message = ""
        # self.compose_message()

        self.template_files = {}
        self.generate_template_files()
        self.template_args = {}
        self.generate_template_args()

        # This flag determines whether there are conflicting file names on the remote repository
        self._remote_repo_valid = False  # call function at beginning of start_new_module script
        # This set of 'valid' flags allows us to call the member functions in whatever order we like, and receive
        # appropriate error messages, without having to repeat checks
        self._can_create_local_module = False  # call function at start
        self._can_push_repo_to_remote = False

    def generate_template_files(self):
        ''' Generates the template files dictionary that can be used to create default module files '''
        self.template_files = obtain_template_files(self.area)

    def generate_template_args(self):
        ''' returns a dictionary that can be used for the .format() method, used in creating files '''
        template_args = {'module': self.module_path, 'getlogin': os.getlogin()}

        self.template_args = template_args

    def verify_remote_repo(self):
        # Creates and uses dir_list to check remote repository for name collisions with new module
        # Raises exception if one currently exists

        exists, dir_path = self._check_if_remote_repo_exists()

        if exists:
            raise VerificationError("The path {dir:s} already exists on gitolite, cannot continue".format(dir=dir_path))

        self._remote_repo_valid = True

    def _check_if_remote_repo_exists(self):

        dir_list = self.get_remote_dir_list()

        for d in dir_list:
            if vcs_git.is_repo_path(d):
                return True, d

        return False, ""

    def get_remote_dir_list(self):
        server_repo_path = self.server_repo_path
        vendor_path = pathf.vendorModule(self.module_path, self.area)
        prod_path = pathf.prodModule(self.module_path, self.area)

        dir_list = [server_repo_path, vendor_path, prod_path]

        return dir_list

    def verify_can_create_local_module(self):
        ''' Determines whether the local directory is a valid starting point for module file structure creation '''
        # Checks that 'we' are not currently in a git repository, and that there are no name conflicts for the files
        # to be created. Returns an exception if these requirements are not met.

        err_message = ""

        mod_dir_exists = os.path.isdir(self.disk_dir)
        cwd_is_repo = vcs_git.is_git_dir()  # true if currently inside git repository
                                            # NOTE: Does not detect if further folder is git repo - how to fix?

        if mod_dir_exists or cwd_is_repo:

            if mod_dir_exists:
                err_message += "Directory {dir:s} already exists, please move elsewhere and try again.\n"

            if cwd_is_repo:
                err_message += "Currently in a git repository, please move elsewhere and try again."

            err_message = err_message.format(dir=os.path.join("./", self.disk_dir)).rstrip()

            self._can_create_local_module = False
            raise VerificationError(err_message)

        self._can_create_local_module = True

    def verify_can_push_repo_to_remote(self):
        ''' Determines whether one can push the local repository to the remote one '''
        # Checks that the folder exists, is a git repository and there are no remote server module path clashes

        err_message = ""
        valid = True

        mod_dir_exists = os.path.isdir(self.disk_dir)  # move to function where creation takes place?

        if not mod_dir_exists:
            err_message += "Directory {dir:s} does not exist.\n"
            valid = False

        else:
            mod_dir_is_repo = vcs_git.is_git_root_dir(self.disk_dir)  # true if folder currently inside git repository
            if not mod_dir_is_repo:
                err_message += "Directory {dir:s} is not a git repository. Unable to push to remote repository.\n"
                valid = False

        err_message = err_message.format(dir=os.path.join("./", self.disk_dir))

        if not self._remote_repo_valid:  # Doing it this way allows us to retain the remote_repo_valid error message
            try:
                self.verify_remote_repo()
            except VerificationError as e:
                err_message += str(e)
                valid = False

        err_message = err_message.rstrip()  # Removes newline character (used for error message concatenation)

        if not valid:
            self._can_push_repo_to_remote = False
            raise VerificationError(err_message)

        self._can_push_repo_to_remote = True

    def create_local_module(self):
        ''' General function that controls the creation of files and folders in a new module. '''
        # cd's into module directory, and creates complete file hierarchy
        # Then creates and commits to a new local repository

        if not self._can_create_local_module:
            self.verify_can_create_local_module()

        self._can_create_local_module = False

        print("Making clean directory structure for " + self.disk_dir)

        if not os.path.isdir(self.disk_dir):
            os.makedirs(self.disk_dir)

        os.chdir(self.disk_dir)  # The reason why we have to chdir into the folder where the files are created is in
        self._create_files()     # order to remain compatible with makeBaseApp.pl, used for IOC and Support modules
        os.chdir(self.cwd)

        vcs_git.init_repo(self.disk_dir)
        vcs_git.stage_all_files_and_commit(self.disk_dir)

    def _create_files(self):
        # Uses makeBaseApp, dls-etc-dir.py and make_files functions depending on area of module
        # Default just sticks to template dictionary entries

        # All classes behave slightly differently

        # self.add_contact() # If contacts exist in the repository, they ought to be added here (or added to dict)
        self._create_files_from_template_dict()

    def _create_files_from_template_dict(self):
        ''' Iterates through the template dict and creates all necessary files and folders '''
        # As dictionaries cannot have more than one key, and the directory does not previously exist, should I
        # error check?

        for path in self.template_files:  # dictionary keys are the relative file paths for the documents
            # Using template_args allows us to insert eg. module name into the file paths in template_files!
            rel_path = path.format(**self.template_args)

            dir_path = os.path.dirname(rel_path)

            if os.path.isfile(rel_path):
                continue  # Stops us from overwriting files in folder (eg. .gitignore for IOC Old-style modules)

            if os.path.normpath(dir_path) == os.path.normpath(rel_path):
                # If folder given instead of file (ie. rel_path ends with a slash or folder already exists)
                raise Exception("{dir:s} in template dictionary is not a valid file name".format(dir=dir_path))
            else:
                if dir_path and not os.path.isdir(dir_path):  # dir_path = '' if eg. "file.txt" given
                    os.makedirs(dir_path)

                open(rel_path, "w").write(self.template_files[path].format(**self.template_args))

    def add_contact(self):
        # Add the module contact to the contacts database
        # Will have to work out where this goes - will it be a part of _create_files or a separate process?
        raise NotImplementedError

    def push_repo_to_remote(self):
        # Pushes the local repo to the remote server.
        if not self._can_push_repo_to_remote:
            self.verify_can_push_repo_to_remote()

        self._can_push_repo_to_remote = False

        vcs_git.add_new_remote_and_push(self.server_repo_path, self.disk_dir)


class NewModuleCreatorTools(NewModuleCreator):

    def print_message(self):

        message_dict = {'module_path': os.path.join(self.disk_dir, self.module_path)}

        message = "\nPlease add your patch files to the {module_path:s} directory"
        message += " and edit {module_path:s}/build script appropriately"
        message = message.format(message_dict)

        print(message)


class NewModuleCreatorPython(NewModuleCreator):

    def print_message(self):

        message_dict = {'module_path': os.path.join(self.disk_dir, self.module_path),
                        'setup_path': os.path.join(self.disk_dir, "setup.py")}

        message = "\nPlease add your python files to the {module_path:s} directory"
        message += " and edit {setup_path} appropriately."
        message = message.format(message_dict)

        print(message)


class NewModuleCreatorWithApps(NewModuleCreator):
    # This is the superclass for all classes that use an app_name variable - for the moment, just Support and IOC
    # These two classes use MakeBaseApp.pl, which creates app_nameApp folders inside the module.

    def __init__(self, module_path, area):
        super(NewModuleCreatorWithApps, self).__init__(module_path, area)
        self.app_name = self.module_name  # sensible default

    def print_message(self):
        # Prints the message. This one is shared between support and IOC

        message_dict = {'RELEASE': os.path.join(self.disk_dir, '/configure/RELEASE'),
            'srcMakefile': os.path.join(self.disk_dir, self.app_name + 'App/src/Makefile'),
            'DbMakefile': os.path.join(self.disk_dir, self.app_name + 'App/Db/Makefile')}

        message = "\nPlease now edit {RELEASE:s} to put in correct paths for dependencies."
        message += "\nYou can also add dependencies to {srcMakefile:s}"
        message += "\nand {DbMakefile:s} if appropriate."
        message = message.format(**message_dict)

        print(message)


class NewModuleCreatorSupport(NewModuleCreatorWithApps):

    def _create_files(self):

        os.system('makeBaseApp.pl -t dls {module:s}'.format(module=self.module_name))
        os.system('dls-make-etc-dir.py && make clean uninstall')
        self._create_files_from_template_dict()


class NewModuleCreatorIOC(NewModuleCreatorWithApps):

    def __init__(self, module_path, app_name, area):

        super(NewModuleCreatorIOC, self).__init__(module_path, area)
        self.app_name = app_name  # Extra argument passed for IOC instantiation

    def _create_files(self):

        os.system('makeBaseApp.pl -t dls {app_name:s}'.format(app_name=self.app_name))
        os.system('makeBaseApp.pl -i -t dls {app_name:s}'.format(app_name=self.app_name))
        shutil.rmtree(os.path.join(self.app_name+'App', 'opi'))
        self._create_files_from_template_dict()


class NewModuleCreatorIOCBL(NewModuleCreatorIOC):  # Note: does NOT inherit from NewModuleCreatorIOC (no shared code)

    def _create_files(self):

        os.system('makeBaseApp.pl -t dlsBL ' + self.app_name)
        self._create_files_from_template_dict()

    def print_message(self):

        message_dict = {'RELEASE': os.path.join(self.disk_dir, '/configure/RELEASE'),
                'srcMakefile': os.path.join(self.disk_dir, self.app_name + 'App/src/Makefile'),
                'DbMakefile': os.path.join(self.disk_dir, self.app_name + 'App/Db/Makefile')}

        message = "\nPlease now edit {RELEASE:s} and path to scripts."
        message += "\nAlso edit {srcMakefile:s} to add all database files from these technical areas."
        message += "\nAn example set of screens has been placed in {DbMakefile:s} . Please modify these.\n"
        message = message.format(**message_dict)

        print(message)


class NewModuleCreatorIOCAddToModule(NewModuleCreatorIOC):
    # Also need:
    # check_remote_repo_valid to look inside module if it exists
    # create_module
    # create_local_repo

    def verify_remote_repo(self):
        # Creates and uses dir_list to check remote repository for name collisions with new module
        # Raises exception if one currently exists
        temp_dir = ""
        try:
            temp_dir = tempfile.mkdtemp()
            vcs_git.clone(self.server_repo_path, temp_dir)

            if os.path.isdir(os.path.join(temp_dir, self.app_name + "App")):
                err_message = "The app {app_name:s} already exists on gitolite, cannot continue"
                raise Exception(err_message.format(app_name=self.app_name))
        except Exception as e:
            raise VerificationError(str(e))  # Also covers exceptions raised by vcs_git.clone, tempfile etc.
        finally:
            if temp_dir:  # If mkdtemp worked
                shutil.rmtree(temp_dir)

        self._remote_repo_valid = True

    def create_local_module(self):
        # clones from the remote repository, then proceeds to input the new files alongside the previously existing ones
        # Then stages and commits (but does not push)

        if not self._can_create_local_module:
            self.verify_can_create_local_module()

        self._can_create_local_module = False

        print("Cloning module to " + self.disk_dir)

        vcs_git.clone(self.server_repo_path, self.disk_dir)

        os.chdir(self.disk_dir)
        self._create_files()
        os.chdir(self.cwd)

        vcs_git.stage_all_files_and_commit(self.disk_dir)

    def push_repo_to_remote(self):
        # Pushes the local repo to the remote server.

        if not self._can_push_repo_to_remote:
            self.verify_can_push_repo_to_remote()

        self._can_push_repo_to_remote = False

        vcs_git.push_to_remote(self.disk_dir)
