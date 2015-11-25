from argparse import ArgumentParser

areas = ["support", "ioc", "matlab", "python", "etc", "tools", "epics"]


class ArgParser(ArgumentParser):

    def __init__(self, usage_v):
        super(ArgParser, self).__init__(description=usage_v)

        self.add_argument(
            "-a", "--area", action="store", type=str, default="support", dest="area",
            help="set <area>=AREA, e.g. " + ", ".join(areas))
        self.add_argument(
            "-p", "--python", action="store_true", dest="python",
            help="set <area>='python'")
        self.add_argument(
            "-i", "--ioc", action="store_true", dest="ioc",
            help="set <area>='ioc'")

    def parse_args(self):
        args = super(ArgParser, self).parse_args()
        # setup area
        if args.ioc:
            args.area = "ioc"
        elif args.python:
            args.area = "python"
        return args
