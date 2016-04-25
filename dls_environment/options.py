from optparse import OptionParser as _OptionParser
from dls_environment import environment


class OptionParser(_OptionParser):
    "options parser with default options for dls svn environment"
    def __init__(self,usage):
        _OptionParser.__init__(self,usage)
        self.add_option("-a", "--area",
            action="store", type="string", dest="area",
            help="set <area>=AREA, e.g. " + ", ".join(environment().areas))
        self.add_option("-p", "--python",
            action="store_true", dest="python", help="set <area>='python'")
        self.add_option("-i", "--ioc",
            action="store_true", dest="ioc", help="set <area>='ioc'")

    def parse_args(self):
        options, args = _OptionParser.parse_args(self)
        # setup area
        if options.ioc:
            options.area = "ioc"
        elif options.python:
            options.area = "python"
        elif not options.area:
            options.area = "support"
        return (options, args)
