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


def make_parser():
    """
    Takes default parser arguments and adds module_name, earlier_release, later_release,
    -v: verbose and -r: raw.

    Returns:
        ArgumentParser: Parser with relevant arguments
    """

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


def colour(word, col, raw):
    """
    Formats <word> in given colour <col> and returns it, unless raw is True

    Args:
        word (str): Text to format
        col (int): Number corresponding to colour
        raw (bool): False if colour to be added, True otherwise

    Returns:
        str: Coloured text or unchanged text if raw is True
    """
    if raw:
        return word
    # >>> I have just hard coded the char conversion of %27c = \x1b in, as I couldn't find the
    # .format equivalent of %c, is anything wrong with this?
    return '\x1b[{col}m{word}\x1b[0m'.format(col=col, word=word)


def create_release_list(repo):
    """
    Get a list of tags of the repository

    Args:
        repo (Repo): Git repository instance

    Returns:
        list: List of tags of repo
    """

    release_list = []
    for tag in repo.tags:
        release_list.append(str(tag))
    return release_list


def format_message_width(message, line_len):
    """
    Takes message and formats each line to be shorter than <line_len>, splits a line into
    multiple lines if it is too long

    Args:
        message (str): Message to format
        line_len (int): Maximum line length to format to

    Returns:
        list: Formatted message as list of message parts shorter than max line length
    """

    if not isinstance(message, list):
        message = [message]
    for i, part in enumerate(message):
        if len(message[i]) > line_len:
            # Find first ' ' before line_len cut-off
            line_end = line_len - message[i][line_len::-1].find(' ')
            # Insert second section to separate list entry
            if ' ' in message[i][line_len::-1]:
                # line_end+1 means the ' ' is not printed at the start of the new line
                message.insert(i+1, message[i][line_end+1:])
            else:
                # Keep string as is if there are no spaces (e.g. long file paths)
                message.insert(i+1, message[i][line_end:])
            # Cut off end of line in original entry
            message[i] = message[i][:line_end]

    return message


def main():

    parser = make_parser()
    args = parser.parse_args()

    blue = 34
    cyan = 36
    green = 32

    e = environment()

    test_list = e.sortReleases([args.earlier_release, args.later_release])
    if args.later_release == test_list[0] and args.later_release != 'HEAD':
        parser.error("<later_release> must be more recent than <earlier_release>")

    pathf.check_technical_area_valid(args, parser)

    source = pathf.devModule(args.module_name, args.area)
    if vcs_git.is_repo_path(source):
        # Get the list of releases from the repo
        if os.path.isdir('./' + args.module_name):
            repo = vcs_git.git.Repo(args.module_name)
            releases = create_release_list(repo)
        else:
            # >>> Use temp_clone once merged
            # repo = vcs_git.temp_clone(source, module)
            vcs_git.clone(source, args.module_name)
            repo = vcs_git.git.Repo(args.module_name)
            # <<<
            releases = create_release_list(repo)
        logging.debug(releases)
    else:
        parser.error("Module " + args.module_name + " doesn't exist in " + source)
        # return so 'releases' can't be referenced before assignment
        return 1

    if args.earlier_release in releases:
        start = args.earlier_release
    else:
        parser.error("Module " + args.module_name + " does not have a release " + args.earlier_release)
    if args.later_release in releases or args.later_release == 'HEAD':
        end = args.later_release
    else:
        parser.error("Module " + args.module_name + " does not have a release " + args.later_release)

    # Get logs between start and end releases in a custom format
    # %h: commit hash, %aD: author date, %cn: committer name, %n: line space, %s: commit message subject,
    # %b: commit message body
    # E.g.:
    #       %h[dfdc111] %aD[Fri, 1 May 2015 14:58:17 +0000] %cn[Ronaldo Mercado]
    #       %s[(re-apply changeset 131625)]
    #       %b[GenericADC cycle parameter default now blank
    #       to prevent accidental "None" strings in startup script][<END>]

    logs = repo.git.log(start + ".." + end, "--format=%h %aD %n%cn %n%s%n%b%n<END>")
    # Add log for start; end is included in start..end but start is not
    logs = logs + '\n' + repo.git.show(start, "--format=%h %aD %n%cn %n%s%n%b")
    # There is an extra line space in the split because one is appended to the front of each entry automatically
    logs = logs.split('\n<END>\n')
    # Sort logs from earliest to latest
    logs.reverse()

    # don't write coloured text if args.raw is True
    if args.raw or \
            (not args.raw and (not sys.stdout.isatty() or os.getenv("TERM") is None or os.getenv("TERM") == "dumb")):
        raw = True
    else:
        raw = False
    
    # Add formatting parameters
    if args.verbose:
        max_line_length = 60
        message_padding = 51
    else:
        max_line_length = 80
        message_padding = 30

    # Make list of logs
    formatted_logs = []
    prev_commit = ''
    for entry in logs:
        commit_hash = entry.split()[0]
        name = '{:<20}'.format(entry.split('\n')[1])

        # Add commit subject message
        commit_message = filter(None, entry.split('\n')[2])
        if len(commit_message) > max_line_length:
            commit_message = format_message_width(commit_message, max_line_length)
            formatted_message = commit_message[0]
            for line in commit_message[1:]:
                formatted_message += '\n' + '{:<{}}'.format('...', message_padding) + line
        else:
            formatted_message = commit_message

        # Check if there is a commit message body and append it
        if len(filter(None, entry.split('\n'))) > 4:
            commit_body = format_message_width(filter(None, entry.split('\n')[3:]), max_line_length - 5)
            for line in commit_body:
                formatted_message += '\n' + '{:<{}}'.format('>>>', message_padding + 5) + line

        # Add date, time and diff info if verbose
        if args.verbose:
            # Add '0' to front of day if only one digit, to keep consistent length
            date = '{:0>2}'.format(entry.split()[2]) + ' ' + entry.split()[3] + ' ' + entry.split()[4]
            time = entry.split()[5]

            formatted_logs.append(colour(commit_hash, blue, raw) + ' ' +
                                  colour(date, cyan, raw) + ' ' +
                                  colour(time, cyan, raw) + ' ' +
                                  colour(name, green, raw) + ': ' + formatted_message)
            if prev_commit:
                diff = repo.git.diff("--name-status", prev_commit, commit_hash)
                if diff:
                    formatted_logs.append("Changes:\n" + diff + '\n')
            prev_commit = commit_hash
        # Otherwise just add to list
        else:
            formatted_logs.append(colour(commit_hash, blue, raw) + ' ' +
                                  colour(name, green, raw) + ': ' + formatted_message)

    print("Log Messages for " + args.module_name + " between releases " + start + " and " + end + ":")

    for log in formatted_logs:
        print(log)


if __name__ == "__main__":
    sys.exit(main())
