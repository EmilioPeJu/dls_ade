from argparse import ArgumentParser
from dls_ade import dls_environment
env = dls_environment.environment()

areas = ["support", "ioc", "matlab", "python", "python3", "python3lib" , "etc", "tools", "epics"]


class ArgParser(ArgumentParser):
    """
    Makes a custom parser class with area arguments by default.

    """
    def __init__(self, usage_v, supported_areas=None):
        super(ArgParser, self).__init__(description=usage_v)

        if supported_areas is None:
            supported_areas = areas

        area = self.add_mutually_exclusive_group(required=False)
        area.add_argument(
            "-a", "--area", action="store", type=str, default="support", dest="area",
            help="Set the area to use",
            choices=supported_areas)
        area.add_argument(
            "-p", "--python", action="store_true", dest="python",
            help="Set 'python' area")
        area.add_argument(
            "-i", "--ioc", action="store_true", dest="ioc",
            help="Set 'ioc' area")
        area.add_argument(
            "--python3", action="store_true", dest="python3",
            help="Set 'python3' area")
        area.add_argument(
            "--python3lib", action="store_true", dest="python3lib",
            help="Set 'python3lib' area")

    def parse_args(self, args=None, namespace=None):
        """
        Parses shortcut flags for setting area; support by default, python if -p, ioc if -i.

        Args:
            args(:class:`argparse.Namespace`): Parser arguments
            namespace(:class:`argparse.Namespace`): Parser namespace

        Returns:
            :class:`argparse.Namespace`: Updated parser arguments

        """
        args = super(ArgParser, self).parse_args(args, namespace)
        # setup area
        if args.ioc:
            args.area = "ioc"
        elif args.python:
            args.area = "python"
        elif args.python3:
            args.area = "python3"
        elif args.python3lib:
            args.area = "python3lib"
        return args

    def add_module_name_arg(self, help_msg="Name of module"):
        """
        Add module_name argument with module specific help message.

        Args:
            help_msg(str): Help message relevant to module calling function
        """

        self.add_argument("module_name", type=str, default="",
                          help=help_msg)

    def add_release_arg(self, help_msg="Release of module", optional=False):
        """
        Add release argument with module specific help message.

        Args:
            help_msg(str): Help message relevant to module calling function
            optional(bool): If True, set release argument to be an optional
            positional argument.

        """
        if not optional:
            self.add_argument("release", type=str, default=None, help=help_msg)
        else:
            self.add_argument("release", nargs='?', type=str, default=None,
                              help=help_msg)

    def add_branch_flag(self, help_msg="Branch of repository"):
        """
        Add branch flag argument with module specific help message.

        Args:
            help_msg(str): Help message relevant to module calling function

        """
        self.add_argument("-b", "--branch", action="store", type=str, dest="branch",
                          help=help_msg)

    def add_git_flag(self, help_msg="Use git repository"):
        """
        Add git flag argument with module specific help message.

        Args:
            help_msg(str): Help message relevant to module calling function

        """
        self.add_argument("-g", "--git", action="store_true", dest="git",
                          help=help_msg)

    def add_epics_version_flag(self, help_msg="Change the epics version, "
                                              "default is " + env.epicsVer() +
                                              " (from your environment)"):
        """
        Add epics version flag argument with module specific help message.

        Args:
            help_msg(str): Help message relevant to module calling function

        """
        self.add_argument("-e", "--epics_version", action="store", type=str, dest="epics_version",
                          default=env.epicsVer(), help=help_msg)

    def add_rhel_version_flag(self, help_msg="Change the rhel version, "
                                             "default is from /etc/redhat-release "
                                             "(can be 6 or 7)"):
        """
        Add rhel version flag argument with module specific help message.

        Args:
            help_msg(str): Help message relevant to module calling function

        """
        self.add_argument("-r", "--rhel_version", action="store", type=str, dest="rhel_version",
                          default=env.rhelVer(), help=help_msg)