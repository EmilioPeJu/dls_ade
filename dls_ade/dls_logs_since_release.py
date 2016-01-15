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


def get_file_changes(commit, prev_commit):

    changed_files = []
    for diff in commit.diff(prev_commit):
        # b_blob corresponds to commit and a_blob to prev_commit
        if diff.b_blob:
            if diff.new_file:
                changed_files.append('A ' + diff.b_blob.path + '\n')
                if diff.renamed:
                    changed_files.append(' (Renamed)')
            else:
                changed_files.append('M ' + diff.b_blob.path + '\n')

        if diff.a_blob and diff.deleted_file:
            changed_files.append('D ' + diff.a_blob.path + '\n')
            if diff.renamed:
                changed_files.append(' (Renamed)')

    return changed_files


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

    # Generate commit messages
    logs = []
    commit_objects = {}
    max_author_length = 0
    for commit in repo.iter_commits(rev=start + ".." + end):
        sha = commit.hexsha[:7]
        author = commit.author
        summary = commit.summary.replace('\n', ' ')
        time_stamp = commit.authored_date
        message = commit.message[len(summary):].replace('\n', ' ')

        ti = time.localtime(commit.authored_date)
        formatted_time = '{:0>2}'.format(ti[2]) + '/' + '{:0>2}'.format(ti[1]) + '/' + str(ti[0]) + ' ' + \
                         '{:0>2}'.format(ti[3]) + ':' + '{:0>2}'.format(ti[4]) + ':' + '{:0>2}'.format(ti[5])

        logs.append([time_stamp, sha, author, summary, formatted_time, message])

        commit_objects[sha] = commit

        # Find longest author name to pad all lines to the same length
        if len(str(author)) > max_author_length:
            max_author_length = len(str(author))

    # Generate tag messages
    for tag in tags_range:
        # Find where info is stored (depends on whether annotated or lightweight tag)
        if hasattr(tag.object, 'author'):
            tag_info = tag.object
        elif hasattr(tag.object.object, 'author'):
            tag_info = tag.object.object
        else:
            # >>> I don't think it will ever get here, but if it does it will be easier to fix with this message.
            raise Exception("Can't find tag info")

        sha = tag.object.hexsha[:7]
        author = str(tag_info.author)
        time_stamp = tag_info.committed_date
        summary = tag_info.summary.replace('\n', ' ') + ' (' + tag.name + ')'
        message = tag_info.message[len(summary):].replace('\n', ' ')

        ti = time.localtime(time_stamp)
        formatted_time = '{:0>2}'.format(ti[2]) + '/' + '{:0>2}'.format(ti[1]) + '/' + str(ti[0]) + ' ' + \
                         '{:0>2}'.format(ti[3]) + ':' + '{:0>2}'.format(ti[4]) + ':' + '{:0>2}'.format(ti[5])

        logs.append([time_stamp, sha, author, summary, formatted_time, message])

        commit_objects[sha] = tag.commit

    # Sort tags and commits chronologically by the UNIX time stamp in index 0
    sorted_logs = sorted(logs, key=itemgetter(0))

    # Check if there are any logs, exit if not
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

    # Make printable list of logs
    formatted_logs = []
    prev_sha = ''
    for log_entry in sorted_logs:
        commit_sha = log_entry[1][:7]
        name = '{:<{}}'.format(log_entry[2], max_author_length)

        # Add commit subject summary
        if log_entry[3]:
            commit_message = format_message_width(log_entry[3], max_line_length)
            formatted_message = commit_message[0]
            for line in commit_message[1:]:
                formatted_message += '\n' + '{:<{}}'.format('...', overflow_message_padding) + line
        else:
            formatted_message = '\n'

        # If verbose add date, time, message body and diff info, then add to logs
        if args.verbose:
            date_and_time = log_entry[4]

            # Check if there is a commit message and append it
            if log_entry[5].strip():
                # The +/- 5 adds an offset for the message body, while maintaining message length
                commit_body = format_message_width(log_entry[5].strip(), max_line_length)
                for line in commit_body:
                    formatted_message += '\n' + '{:<{}}'.format('...', overflow_message_padding) + line

            # Get diff information for each commit >>> Diff info separate from formatted message
            if prev_sha:
                changed_files = get_file_changes(commit_objects[prev_sha], commit_objects[commit_sha])
                if changed_files:
                    formatted_message += "\n\nChanges:\n"
                    for file_change in changed_files:
                        formatted_message += file_change
            prev_sha = commit_sha

            formatted_logs.append(colour(commit_sha, blue, raw) + ' ' +
                                  colour(date_and_time, cyan, raw) + ' ' +
                                  colour(name, green, raw) + ': ' + formatted_message)
        # Otherwise, add to logs
        else:
            formatted_logs.append(colour(commit_sha, blue, raw) + ' ' +
                                  colour(name, green, raw) + ': ' + formatted_message)

    # Switch to reverse chronological order
    formatted_logs.reverse()

    print("Log Messages for " + args.module_name + " between releases " + start + " and " + end + ":")
    for log in formatted_logs:
        print(log)

    shutil.rmtree(repo.working_tree_dir)


if __name__ == "__main__":
    sys.exit(main())
