import argparse
import variables

parser = argparse.ArgumentParser()


class ArgumentParser(parser):

    def __init__(self, usage):

        parser.__init__(self, usage)

        self.add_argument("-a", "--area",
            action="store", type="string", dest="area",
            help="set <area>=AREA, e.g. " + ", ".join(variables.areas))
        self.add_argument("-p", "--python",
            action="store_true", dest="python", help="set <area>='python'")
        self.add_argument("-i", "--ioc",
            action="store_true", dest="ioc", help="set <area>='ioc'")

    def parse_args(self):
        options, args = parser.parse_args(self)
        # setup area
        if options.ioc:
            options.area = "ioc"
        elif options.python:
            options.area = "python"
        elif not options.area:
            options.area = "support"
        return (options, args)
