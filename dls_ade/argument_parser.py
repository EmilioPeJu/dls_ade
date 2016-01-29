from argparse import ArgumentParser

areas = ["support", "ioc", "matlab", "python", "etc", "tools", "epics"]


class ArgParser(ArgumentParser):

    def __init__(self, usage_v):
        super(ArgParser, self).__init__(description=usage_v)

        area = self.add_mutually_exclusive_group(required=True)
        area.add_argument(
            "-a", "--area", action="store", type=str, default="support", dest="area",
            help="set <area>=AREA, e.g. " + ", ".join(areas))
        area.add_argument(
            "-p", "--python", action="store_true", dest="python",
            help="set <area>='python'")
        area.add_argument(
            "-i", "--ioc", action="store_true", dest="ioc",
            help="set <area>='ioc'")

    def parse_args(self, args=None, namespace=None):
        args = super(ArgParser, self).parse_args(args, namespace)
        # setup area
        if args.ioc:
            args.area = "ioc"
        elif args.python:
            args.area = "python"
        return args

    def add_module(self, help_msg):
        pass
