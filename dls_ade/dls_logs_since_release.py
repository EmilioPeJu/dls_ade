#!/bin/env dls-python
# This script comes from the dls_scripts python module

import os
import sys
import time
from argument_parser import ArgParser
from dls_environment import environment
import path_functions as pathf
import vcs_git

usage = """
Default <area> is 'support'.
Print all the log messages for module <module_name> in the <area> area of svn
from the revision number when <earlier_release> was done, to the revision
when <later_release> was done. If not specified, <earlier_release> defaults to
revision 0, and <later_release> defaults to the head revision. If
<earlier_release> is given an invalid value (like 'latest') if will be set
to the latest release.
"""

RED = 31
BLUE = 34
# Unused colours
BLACK = 30
GREEN = 32
YELLOW = 33
MAGENTA = 35
CYAN = 36
GREY = 37


def make_parser():

    parser = ArgParser(usage)
    parser.add_argument(
        "module_name", type=str, default=None,
        help="name of module")
    parser.add_argument(
        "earlier_release", type=int, default=0,
        help="start point of log messages")
    parser.add_argument(
        "later_release", type=int, default="Set to Head",
        help="end point of log messages")
    parser.add_argument(
        "-v", "--verbose", action="store_true", dest="verbose",
        help="Print lots of log information")
    parser.add_argument(
        "-r", "--raw", action="store_true", dest="raw",
        help="Print raw text (not in colour)")

    return parser


def check_technical_area_valid(args, parser):

    if args.area == "ioc" and not len(args.module.split('/')) > 1:
        parser.error("Missing Technical Area Under Beamline")


def colour(word, col, raw):
    if raw:
        return word
    # >>> I have just hard coded the char conversion of %27c in, as I couldn't find the
    # .format equivalent of %c, is anything wrong with this?
    return '\x1b[{col}m{word}\x1b[0m'.format(col=col, word=word)


def main():

    sys.path.append("..")

    parser = make_parser()
    args = parser.parse_args()

    e = environment()

    # don't write coloured text if args.raw (it confuses less)
    if args.raw or \
            (not args.raw and (not sys.stdout.isatty() or os.getenv("TERM") is None or os.getenv("TERM") == "dumb")):
        raw = True
    else:
        raw = False

    # module is 'everything', list logs for entire area
    if args.module == 'everything':
        module = args.area  # >>> This isn't very clear later on
        source = pathf.devArea(args.area)
        release = pathf.prodArea(args.area)
        # release = e.prodArea
    else:
        # otherwise check logs for specific module
        check_technical_area_valid(args, parser)
        module = args.module
        source = pathf.devModule(module, args.area)
        release = pathf.prodModule(module, args.area)
        # release = e.prodModule
    
    # Work out the initial and end release numbers
    start = svn.Revision(svn.opt_revision_kind.number, 0)
    end = svn.Revision(svn.opt_revision_kind.head)    

    # Check for existence of this module in various places in the repository
    # and note revisions
    if not vcs_git.is_repo_path(source):
        parser.error("Repository does not contain " + source)
    
    if vcs_git.is_repo_path(release):
        release_dir = release.replace(svn.info2(release, recurse=False)[0][1]["repos_root_URL"], "")
        # Remove unicode attribute from release_dir so that it doesn't propagate
        # into other values and cause unexpected decode failures.
        release_dir = str(release_dir)

        # Now grab the logs from the release dir
        r_logs = svn.log(release, discover_changed_paths=True)

        early_num = args.earlier_release
        releases = []
        # Create a list of release numbers and their created dates
        for log in r_logs:
            if log["changed_paths"]:
                for pdict in log["changed_paths"]:
                    if pdict["action"].upper() == "A":
                        rnum = pdict["path"].replace(release_dir, "").lstrip("/")
                        if rnum and "/" not in rnum and pdict["copyfrom_revision"]:
                            releases = [(r, l) for r, l in releases if r != rnum] +\
                                       [(rnum, pdict["copyfrom_revision"])]
        # Sort them by rev
        releases = [(r, l) for _, r, l in sorted([(l.number, r, l) for r, l in releases])]

        # adjust the start rev to be early_release
        i = 0
        while i < len(releases) and releases[i][0] != early_num:
            i += 1
        if i == len(releases):
            i = -1
            print("Repository does not contain " + early_num +
                  ", using latest release " + releases[-1][0])

        start = releases[i][1]

        late_num = args.later_release
        j = len(releases) - 1
        while j > 0 and releases[j][0] != late_num:
            j -= 1
        if j == 0:
            print("Repository does not contain '" + late_num + "', using head'")
        else:
            end = svn.Revision(svn.opt_revision_kind.number,
                                releases[j][1].number + 1)
        r_logs = svn.log(release, revision_start=start, revision_end=end, discover_changed_paths=True)
    else:
        parser.error(module + " doesn't exist in " + release)
    
    # now grab the logs from the 2 dirs
    logs = svn.log(source, revision_start=start, revision_end=end, discover_changed_paths=args.verbose)

    for l in r_logs:
        l["message"] += \
            " (Release dir %s)" % l["changed_paths"][0]["path"].replace(release_dir, "").lstrip("/")
        if l["changed_paths"][0]["copyfrom_revision"]:
            # hack the revision so it's a little later than the copy from location

            # >>> WHAT IS THIS?

            class rev:
                number = l["changed_paths"][0]["copyfrom_revision"].number + 0.1            
            l["revision"] = rev()
    
    # intersperse them
    ll = [(l["revision"].number, l) for l in r_logs]
    ll += [(l["revision"].number, l) for l in logs if l["revision"].number > start.number]    
    logs = [l[1] for l in reversed(sorted(ll))]

    # Now print them
    print("Log Messages:")
    for log in logs:
        message = log["message"].split(module+":", 1)
        if len(message) == 1:
            message = message[0].strip()
        else:
            message = message[1].strip()
        rev = "(r{0})".format(int(log["revision"].number))
        # Align print columns using {:(17 - len(rev)}
        pre = "{:{}} {}:".format(log["author"], 17 - len(rev), rev)
        if args.verbose:
            header = "{0} {1}".format(pre, time.ctime(log["date"]))
            print(colour(header, RED, raw))
            print(colour("-" * min(80, len(header)), RED, raw))
            print(message)
            if log["changed_paths"]:
                print("Changes:")
                for change in log["changed_paths"]:
                    print("  {0} {1}".format(change["action"], change["path"]))
                print("")
            print("")
        else:
            print("{0} {1}".format(colour(pre, RED, raw), message))

if __name__ == "__main__":
    sys.exit(main())
