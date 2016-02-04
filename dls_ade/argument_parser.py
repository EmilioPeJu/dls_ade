from argparse import ArgumentParser
from dls_ade import dls_environment
env = dls_environment.environment()

areas = ["support", "ioc", "matlab", "python", "etc", "tools", "epics"]


class ArgParser(ArgumentParser):
    """
    Makes a custom parser class with area arguments by default.

    """

    def __init__(self, usage_v, applicable_areas=areas):
        super(ArgParser, self).__init__(description=usage_v)

        area = self.add_mutually_exclusive_group(required=False)
        area.add_argument(
            "-a", "--area", action="store", type=str, default="support", dest="area",
            help="Set area, e.g. " + ", ".join(applicable_areas))
        area.add_argument(
            "-p", "--python", action="store_true", dest="python",
            help="Set 'python' area")
        area.add_argument(
            "-i", "--ioc", action="store_true", dest="ioc",
            help="Set 'ioc' area")

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
        return args

    def add_module_name_arg(self, help_msg="Name of module"):
        """
        Add module_name argument with module specific help message.

        Args:
            help_msg: Help message relevant to module calling function

        """
        self.add_argument("module_name", type=str, default=None,
                          help=help_msg)

    def add_release_arg(self, help_msg="Release of module"):
        """
        Add release argument with module specific help message.

        Args:
            help_msg: Help message relevant to module calling function

        """
        self.add_argument("release", type=str, default=None,
                          help=help_msg)

    def add_branch_flag(self, help_msg="Branch of repository"):
        """
        Add branch flag argument with module specific help message.

        Args:
            help_msg: Help message relevant to module calling function

        """
        self.add_argument("-b", "--branch", action="store", type=str, dest="branch",
                          help=help_msg)

    def add_git_flag(self, help_msg="Use git repository"):
        """
        Add git flag argument with module specific help message.

        Args:
            help_msg: Help message relevant to module calling function

        """
        self.add_argument("-g", "--git", action="store_true", dest="git",
                          help=help_msg)

    def add_epics_version_flag(self, help_msg="Change the epics version, "
                                              "default is " + env.epicsVer() +
                                              " (from your environment)"):
        """
        Add epics version flag argument with module specific help message.

        Args:
            help_msg: Help message relevant to module calling function

        """
        self.add_argument("-e", "--epics_version", action="store", type=str, dest="epics_version",
                          help=help_msg)
