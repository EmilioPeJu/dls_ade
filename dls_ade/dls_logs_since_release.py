#!/bin/env dls-python
# This script comes from the dls_scripts python module

import os
import sys
import shutil
import time
from operator import itemgetter
from argument_parser import ArgParser
from dls_environment import environment
import path_functions as pathf
import vcs_git
import logging

logging.basicConfig(level=logging.WARNING)

usage = """
Default <area> is 'support'.
Print all the log messages for module <module_name> in the <area> area of svn
from the revision number when <earlier_release> was done, to the revision
when <later_release> was done. If not specified, <earlier_release> defaults to
revision the most recent release, and <later_release> defaults to the head revision.
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
        "-e", "--earlier_release", action="store", dest="earlier_release", type=str,
        help="start point of log messages")
    parser.add_argument(
        "-l", "--later_release", action="store", dest="later_release", type=str,
        help="end point of log messages")
    parser.add_argument(
        "-v", "--verbose", action="store_true", dest="verbose",
        help="Adds date, time and file diff information to logs")
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
            # Insert second section to separate list entry
            if ' ' in message[i][line_len::-1]:
                # Find first ' ' before line_len cut-off
                line_end = line_len - message[i][line_len::-1].find(' ')
                # line_end+1 means the ' ' is not printed at the start of the new line
                message.insert(i+1, message[i][line_end+1:])
            else:
                # Don't remove characters if there are no spaces (e.g. long file paths)
                line_end = line_len
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

    # If earlier_releases and later_releases both provided then check that later_* comes after earlier_*
    if args.earlier_release and args.later_release:
        test_list = e.sortReleases([args.earlier_release, args.later_release])
        if args.later_release == test_list[0] and args.later_release != 'HEAD':
            parser.error("<later_release> must be more recent than <earlier_release>")

    pathf.check_technical_area_valid(args.area, args.module_name)

    source = pathf.devModule(args.module_name, args.area)
    if vcs_git.is_repo_path(source):
        # Get the list of releases from the repo
        print("Cloning " + args.module_name + " from " + args.area + " area...")
        repo = vcs_git.temp_clone(source)
        releases = create_release_list(repo)
        logging.debug(releases)
    else:
        raise Exception("Module " + args.module_name + " doesn't exist in " + source)

    # Set earlier_releases and later_releases to defaults if not provided
    if not args.later_release:
        later = 'HEAD'
    else:
        later = args.later_release
    if not args.earlier_release:
        # If later_release specified then print from first release to that point.
        # If later_release is not specified, print logs since (most recent) release
        if later == 'HEAD':
            earlier = releases[-1]
        else:
            earlier = releases[0]
    else:
        earlier = args.earlier_release

    # Check that given releases exist
    if earlier in releases:
        start = earlier
    else:
        raise Exception("Module " + args.module_name + " does not have a release " + args.earlier_release)
    if later in releases or later == 'HEAD':
        end = later
    else:
        raise Exception("Module " + args.module_name + " does not have a release " + args.later_release)

    # Get list of tag objects in required range
    tags = []
    tag_refs = []
    for tag in repo.tags:
        tag_refs.append(tag)
        tags.append(str(tag))
    if later == 'HEAD':
        # If later is HEAD then just go to most recent release
        tags_range = tag_refs[tags.index(start):tags.index(releases[-1])+1]
    else:
        tags_range = tag_refs[tags.index(start):tags.index(end)+1]
    logging.debug(tags_range)

    logs = []
    for commit in repo.iter_commits(rev=start + ".." + end):
        sha = commit.hexsha
        author = commit.author
        message = commit.summary
        time_stamp = commit.authored_date

        ti = time.localtime(commit.authored_date)
        formatted_time = '{:0>2}'.format(ti[2]) + '/' + '{:0>2}'.format(ti[1]) + '/' + str(ti[0]) + ' ' + \
                         '{:0>2}'.format(ti[3]) + ':' + '{:0>2}'.format(ti[4]) + ':' + '{:0>2}'.format(ti[5])

        logs.append([time_stamp, sha, author, formatted_time, message])

    for tag in tags_range:
        sha = tag.object.hexsha
        if hasattr(tag.object, 'author'):
            author = str(tag.object.author)
            time_stamp = tag.object.committed_date
            summary = tag.object.summary + ' (' + tag.name + ')'
            message = tag.object.message[len(summary):]
        elif hasattr(tag.object.object, 'author'):
            author = str(tag.object.object.author)
            time_stamp = tag.object.object.committed_date
            summary = tag.object.object.summary + ' (' + tag.name + ')'
            message = tag.object.object.message[len(summary):]

        ti = time.localtime(time_stamp)
        formatted_time = '{:0>2}'.format(ti[2]) + '/' + '{:0>2}'.format(ti[1]) + '/' + str(ti[0]) + ' ' + \
                         '{:0>2}'.format(ti[3]) + ':' + '{:0>2}'.format(ti[4]) + ':' + '{:0>2}'.format(ti[5])

        logs.append([time_stamp, sha, author, formatted_time, summary, message])

    sorted_logs = sorted(logs, key=itemgetter(0))

    if not sorted_logs:
        print("No logs for " + args.module_name + " between releases " +
              args.earlier_release + " and " + args.later_release)
        return 0

    # Don't write coloured text if args.raw is True
    if args.raw or \
            (not args.raw and (not sys.stdout.isatty() or os.getenv("TERM") is None or os.getenv("TERM") == "dumb")):
        raw = True
    else:
        raw = False

    # Find longest author name to pad all lines to the same length
    log_summary = repo.git.shortlog(start + ".." + end, '-s', '-n').split('\n')
    logging.debug(log_summary)
    # ['   129\tRonaldo Mercado', '     9\tJames Rowland', '     5\tIan Gillingham']
    if filter(None, log_summary):
        author_list = []
        logging.debug(author_list)
        for log_entry in log_summary:
            author_list.append(log_entry.split('\t')[1])
        max_author_length = 0
        for author in author_list:
            logging.debug(author)
            if len(author) > max_author_length:
                max_author_length = len(author)
                logging.debug(max_author_length)
        # Add a space before the ':' on the longest author (Just for appearance)
        max_author_length += 1
    else:
        # If no author information is generated, set length to default
        max_author_length = 20

    # Add formatting parameters
    screen_width = 100
    if args.verbose:
        # len("e38e73a 01/05/2015 17:20:46 " + ": ") = 30
        overflow_message_padding = max_author_length + 30
        max_line_length = screen_width - overflow_message_padding
    else:
        # len("e38e73a " + ": ") = 10
        overflow_message_padding = max_author_length + 10
        max_line_length = screen_width - overflow_message_padding

    # logs.append([time_stamp, sha, author, formatted_time, summary, message])

    # Make list of logs
    formatted_logs = []
    prev_commit = ''
    for log_entry in sorted_logs:
        commit_hash = log_entry[1][:7]
        name = '{:<{}}'.format(log_entry[2], max_author_length)

        # Add commit subject message
        if log_entry[4]:
            commit_message = format_message_width(log_entry[4], max_line_length)
            formatted_message = commit_message[0]
            for line in commit_message[1:]:
                formatted_message += '\n' + '{:<{}}'.format('...', overflow_message_padding) + line
        else:
            formatted_message = '\n'

        # Add date, time and diff info if verbose
        if args.verbose:
            date_and_time = log_entry[3]

            formatted_logs.append(colour(commit_hash, blue, raw) + ' ' +
                                  colour(date_and_time, cyan, raw) + ' ' +
                                  colour(name, green, raw) + ': ' + formatted_message)

            # Check if there is a commit message body and append it
            if log_entry[5]:
                # The +/- 5 adds an offset for the message body, while maintaining message length
                commit_body = format_message_width(log_entry[5], max_line_length - 5)
                for line in commit_body:
                    formatted_message += '\n' + '{:<{}}'.format('>>>', overflow_message_padding + 5) + line

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

    shutil.rmtree(repo.working_tree_dir)


if __name__ == "__main__":
    sys.exit(main())
