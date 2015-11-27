
def new_module_generator(args, cwd):
    # Use arguments to determine which new module creator to use, and return it

    # List of classes:
        # NewModuleIOC
        # NewModuleIOC-BL(NewModuleIOC)

        # NewModulePython
        # NewModuleSupport - very few changes
        # NewModuleTools - very few changes
    pass


class NewModuleCreator:

    def __init__(self, module, area, cwd):
        # Initialise all private variables, including:
            # template list - include variable list for .format()?
            # module name
            # area
            # disk directory - directory where module to be imported is located
            # app name
            # If IOC:
                # technical area
            # dest - location of file on server
        pass

    def check_remote_repo(self):
        # Creates and uses dir_list to check remote repository for name collisions with new module - part of init?
        pass

    def check_local_repo(self):
        # Checks that 'we' are not currently in a git repository, and that there are no name conflictions for the files
        # to be created
        pass

    def message_generator(self):
        # Generates the message to print out to the user on creation of the module files
        pass

    def file_generation(self):
        # Creates the files (possibly in subdirectories) as part of the module creation process
        # Part of this involves chdir into the module directory, and exiting at the end of the process
        # Uses makeBaseApp, dls-etc-dir.py and make_files functions depending on area of module

        # Likely virtual, as all classes behave slightly differently
        pass

    def gitignore_generation(self):
        # Generates .gitignore file. Could be part of file_generation
        pass

    def print_messages(self):
        # Prints the messages previously constructed. Could move message creation after file generation
        # Move the print statement from make_files_tools to here!
        pass

    def stage_and_commit(self):
        # Stages and commits the files to the local repository. Separate from export repo as export not always done!
        # Switch statement in export?
        pass

    def push_repo_to_remote(self):
        # Pushes the local repo to the remote server.
        pass

