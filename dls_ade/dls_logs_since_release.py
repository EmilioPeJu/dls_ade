#!/bin/env dls-python
# This script comes from the dls_scripts python module

import os
import sys
from argument_parser import ArgParser
from dls_environment import environment
import path_functions as pathf
import vcs_git
import logging

logging.basicConfig(level=logging.DEBUG)

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
        "earlier_release", type=str, default='0',
        help="start point of log messages")
    parser.add_argument(
        "later_release", type=str, default='1',
        help="end point of log messages")
    parser.add_argument(
        "-v", "--verbose", action="store_true", dest="verbose",
        help="Print lots of log information")
    parser.add_argument(
        "-r", "--raw", action="store_true", dest="raw",
        help="Print raw text (not in colour)")

    return parser


def check_technical_area_valid(args, parser):

    if args.area == "ioc" and not len(args.module_name.split('/')) > 1:
        parser.error("Missing Technical Area Under Beamline")


def colour(word, col, raw):
    if raw:
        return word
    # >>> I have just hard coded the char conversion of %27c in, as I couldn't find the
    # .format equivalent of %c, is anything wrong with this?
    return '\x1b[{col}m{word}\x1b[0m'.format(col=col, word=word)


def create_release_list(repo):

    release_list = []
    for tag in repo.tags:
        info = repo.git.show(tag)
        for i, entry in enumerate(info.split()):
            if entry == "Date:":
                date = info.split()[i+3] + ' ' + info.split()[i+2] + ' ' + info.split()[i+5]
                break
        release_list.append((str(tag), date))
    return release_list


def main():

    parser = make_parser()
    args = parser.parse_args()

    e = environment()
    test_list = e.sortReleases([args.earlier_release, args.later_release])
    if args.later_release == test_list[0]:
        parser.error("<later_release> must be more recent than <earlier_release>")

    # don't write coloured text if args.raw
    if args.raw or \
            (not args.raw and (not sys.stdout.isatty() or os.getenv("TERM") is None or os.getenv("TERM") == "dumb")):
        raw = True
    else:
        raw = False

    # If module is 'everything', list logs for entire area >>> Is this used? It will be a little difficult to implement.
    if args.module_name == 'everything':
        module = args.area  # >>> This isn't very clear later on
        source = pathf.devArea(args.area)
        # release = pathf.prodArea(args.area)
    else:
        # otherwise check logs for specific module
        check_technical_area_valid(args, parser)
        module = args.module_name
        source = pathf.devModule(module, args.area)
        # release = pathf.prodModule(module, args.area)

    if not vcs_git.is_repo_path(source):
        parser.error("Repository does not contain " + source)

    if vcs_git.is_repo_path(source):

        # Get the list of releases from the repo
        if os.path.isdir('./' + module):
            repo = vcs_git.git.Repo(module)
            releases = create_release_list(repo)
        else:
            vcs_git.clone(source, module)
            repo = vcs_git.git.Repo(module)
            releases = create_release_list(repo)

        for entry in releases:
            if args.earlier_release == entry[0]:
                start = entry[0]
            if args.later_release == entry[0]:
                end = entry[0]
    else:
        parser.error("Module " + module + " doesn't exist in " + source)

    # Get logs between start and end releases with custom format
    # %h: commit hash, %aD: author date, %cn: committer name, %n: line space, %s: commit message subject,
    # >>> %body: commit message body

    # Lots of line spacings in case someone puts line spacings at end of a commit message and ruins the splitting
    logs = repo.git.log(start + ".." + end, "--format=%h %aD %cn %n %s %n %b %n%n%n%n%n")
    # Add log for start -- end is included in start..end but start is not
    logs = logs + '\n' + repo.git.show(start, "--format=%h %aD %cn %n %s %n %b")
    # There is one extra line space in the split because one is appended to the front of each entry automatically
    logs = logs.split('\n\n\n\n\n\n')

    logs.reverse()

    formatted_logs = []
    prev_commit = ''
    for entry in logs:
        commit = entry.split()[0]

        name = '{:<20}'.format(entry.split()[7] + ' ' + entry.split()[8])

        message = entry.split('\n')[1]
        if len(entry.split('\n')) > 3:
            for sub_entry in entry.split('\n')[2:]:
                if sub_entry:
                    message = message + '\n' + '{:>30}'.format(sub_entry)

        if args.verbose:

            if len(entry.split()[2]) == 1:
                date = '0' + entry.split()[2] + ' ' + entry.split()[3] + ' ' + entry.split()[4]
            else:
                date = entry.split()[2] + ' ' + entry.split()[3] + ' ' + entry.split()[4]

            time = entry.split()[5]

            formatted_logs.append(colour(commit, BLUE, raw) + ' ' + colour(date, CYAN, raw) + ' ' +
                                  colour(time, CYAN, raw) + ' ' + colour(name, GREEN, raw) + ': ' + message)

            if prev_commit:
                diff = repo.git.diff("--name-status", prev_commit, commit)
                if diff:
                    formatted_logs.append("Changes:\n" + diff + '\n')
            prev_commit = commit
        else:
            formatted_logs.append(colour(commit, BLUE, raw) + ' ' + colour(name, GREEN, raw) + ': ' + message)

    print("Log Messages for " + module + " between releases " + start + " and " + end + ":")

    for log in formatted_logs:
        print(log)


if __name__ == "__main__":
    sys.exit(main())
