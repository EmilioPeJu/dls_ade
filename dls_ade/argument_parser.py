from argparse import ArgumentParser as _Parser
import variables


class ArgumentParser(_Parser):

    def __init__(self, usage):
        _Parser.__init__(self, usage)

        self.add_argument("-a", "--area",
            action="store", type=str, default="support", dest="area",
            help="set <area>=AREA, e.g. " + ", ".join(variables.areas))
        self.add_argument("-p", "--python",
            action="store_true", dest="python", help="set <area>='python'")
        self.add_argument("-i", "--ioc",
            action="store_true", dest="ioc", help="set <area>='ioc'")

    def parse_args(self):
        options = _Parser.parse_args(self)
        print options
        # setup area
        if options.ioc:
            options.area = "ioc"
        elif options.python:
            options.area = "python"
        return options

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.parse_args()
