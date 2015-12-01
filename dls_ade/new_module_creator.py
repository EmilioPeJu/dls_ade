import os


def get_new_module_creator(args):
    # Use arguments to determine which new module creator to use, and return it

    # Validate whether area type is supported!

    # List of classes:
        # NewModuleIOC
        # NewModuleIOC-BL(NewModuleIOC)

        # NewModulePython
        # NewModuleSupport - very few changes
        # NewModuleTools - very few changes
    #

    if args.area not in ("ioc", "support", "tools", "python"):
        raise Exception("Don't know how to make a module of type " + args.area)

    module = args.module_name
    area = args.area
    cwd = os.getcwd()

    if args.area == "ioc":
        area = "ioc"
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

        return NewModuleCreatorIOC(module, area, cwd)
    elif args.area == "python":
        return NewModuleCreatorPython(module, area, cwd)
    elif args.area == "support":
        return NewModuleCreatorSupport(module, area,cwd)
    elif args.area == "tools":
        return NewModuleCreatorTools(module, area, cwd)

    # TODO Finish function


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

        raise NotImplementedError

    def check_remote_repo(self):
        # Creates and uses dir_list to check remote repository for name collisions with new module - part of init?
        raise NotImplementedError

    def check_local_repo(self):
        # Checks that 'we' are not currently in a git repository, and that there are no name conflictions for the files
        # to be created
        raise NotImplementedError

    def message_generator(self):
        # Generates the message to print out to the user on creation of the module files
        raise NotImplementedError

    def create_files(self):
        # Creates the files (possibly in subdirectories) as part of the module creation process
        # Part of this involves chdir into the module directory, and exiting at the end of the process
        # Uses makeBaseApp, dls-etc-dir.py and make_files functions depending on area of module

        # Likely abstract, as all classes behave slightly differently
        raise NotImplementedError

    def create_gitignore(self):
        # Generates .gitignore file. Could be part of file_generation - part of super()?
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


class NewModuleCreatorIOC(NewModuleCreator):

    def __init__(self, module, area, cwd, technical_area):
        super(NewModuleCreatorIOC, self).__init__(self, module, area, cwd)
        # Initialise all private variables, including:
            # template list - include variable list for .format()?
            # module name
            # area
            # disk directory - directory where module to be imported is located
            # app name
            # If IOC:
                # technical area
            # dest - location of file on server

        raise NotImplementedError

    pass


class NewModuleCreatorIOCBL(NewModuleCreatorIOC):
    pass


class NewModuleCreatorPython(NewModuleCreator):
    pass


class NewModuleCreatorSupport(NewModuleCreator):
    pass


class NewModuleCreatorTools(NewModuleCreator):
    pass
