#!/bin/env dls-python
# This script comes from the dls_scripts python module

from __future__ import unicode_literals
import os
import sys
import shutil
import time
from operator import itemgetter
from dls_ade.argument_parser import ArgParser
from dls_ade.dls_environment import environment
from dls_ade import path_functions as pathf
from dls_ade import vcs_git
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
        help="Name of module")
    parser.add_argument(
        "releases", nargs='*', type=str, default=None,
        help="Releases range to print logs for")
    parser.add_argument(
        "-e", "--earlier_release", action="store", dest="earlier_release", type=str,
        help="Start point of log messages")
    parser.add_argument(
        "-l", "--later_release", action="store", dest="later_release", type=str,
        help="End point of log messages")
    parser.add_argument(
        "-v", "--verbose", action="store_true", dest="verbose",
        help="Adds date, time, message body and file diff information to logs")
    parser.add_argument(
        "-r", "--raw", action="store_true", dest="raw",
        help="Print raw text (not in colour)")

    return parser


def set_raw_argument(raw):
    """
    Set raw to True or False based on parsed arguments and environment

    Args:
        raw: Parser argument allowing user to decide to print in raw

    Returns:
        True or False to print in raw or not

    """
    # Don't write coloured text if args.raw is True
    if raw or \
            (not raw and (not sys.stdout.isatty() or os.getenv("TERM") is None or os.getenv("TERM") == "dumb")):
        return True
    else:
        return False


def check_parsed_args_compatible(releases, earlier, later, parser):
    """
    Check that releases range is specified in the correct way

    Args:
        releases: a list of two releases; the start and end point
        earlier: the start point to print up until HEAD
        later: the end point to print up to from first release
        parser: ArgParse instance to handle error

    Raises:
        ArgParse Error: To specify both start and end point, use format
        (e.g.) 'ethercat 3-1 4-1', not -l and -e flags.

    """
    if (releases and earlier) or \
            (releases and later) or \
            (earlier and later):
        parser.error("To specify both start and end point, use format "
                     "(e.g.) 'ethercat 3-1 4-1', not -l and -e flags.")


def check_releases_valid(releases, parser):
    """
    Check that two releases given and in correct order

    Args:
        releases: releases range
        parser: ArgParse instance to handle error

    Raises:
        ArgParse Error:
            [If one release given]: To specify just start or just end point, use -e or -l flag.
            [If more than two releases given]: Only two releases can be specified (start and end point)
            [If releases in wrong order]: Input releases in correct order (<earlier_release> <later_release>)

    """
    if len(releases) == 1:
        parser.error("To specify just start or just end point, use -e or -l flag.")
    if len(releases) > 2:
        parser.error("Only two releases can be specified (start and end point)")
    elif len(releases) == 2:
        # If start and end points both provided then check that later comes after earlier
        env = environment()
        test_list = env.sortReleases([releases[0], releases[1]])
        if releases[1] == test_list[0] and releases[1] != 'HEAD':
            parser.error("Input releases in correct order (<earlier_release> <later_release>)")


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
        release_list.append(tag.name)
    return release_list


def set_log_range(module, releases, earlier, later, releases_list):
    """
    Set range to get logs for from parsed args or defaults if not given

    Args:
        module: module to get logs for
        releases: releases range
        earlier: specified start point
        later: specified end point
        releases_list: list of releases from repository

    Raises:
        ValueError: Module <module> does not have a release <start>/<end>
    Returns:
        start and end point to list releases for

    """
    if releases and len(releases) == 2:
        start = releases[0]
        end = releases[1]
    elif earlier:
        start = earlier
        end = 'HEAD'
    elif later:
        start = releases_list[0]
        end = later
    else:
        start = releases_list[0]
        end = 'HEAD'

    # Check that releases exist
    if start not in releases_list:
        raise ValueError("Module " + module + " does not have a release " + start)
    if end not in releases_list and end != 'HEAD':
        raise ValueError("Module " + module + " does not have a release " + end)

    return start, end


def get_log_messages(repo, start, end):
    """
    Create a log_info dictionary and add log messages, commit objects and max author length

    Args:
        repo: git repository instance
        start: start point of logs
        end: end point of logs

    Returns:
        Dictionary containing messages, commit objects and the longest author name

    """
    log_info = {'logs': [], 'commit_objects': {}, 'max_author_length': 0}

    for commit in repo.iter_commits(rev=start + ".." + end):
        sha = commit.hexsha[:7]
        author = commit.author.name
        summary = commit.summary.replace('\n', ' ')
        time_stamp = commit.authored_date
        message = commit.message[len(summary):].replace('\n', ' ')

        formatted_time = convert_time_stamp(time_stamp)

        log_info['logs'].append([time_stamp, sha, author, summary, formatted_time, message])

        # Add to dictionary of commit objects for creating diff info later
        log_info['commit_objects'][sha] = commit

        # Find longest author name to pad all lines to the same length
        if len(author) > log_info['max_author_length']:
            log_info['max_author_length'] = len(author)

    return log_info


def get_tags_list(repo, start, end, last_release):
    """
    Get a list of tags from the repo and return the require range

    Args:
        repo: git repository instance
        start: start point of tags
        end: end point of tags
        last_release: most recent release of module

    Returns:
        list of tags in required range

    """
    tags = []
    tag_refs = []
    for tag in repo.tags:
        tag_refs.append(tag)
        tags.append(tag.name)

    if end == 'HEAD':
        # If end is HEAD then just go up to most recent release with tags
        tags_range = tag_refs[tags.index(start):tags.index(last_release)+1]
    else:
        tags_range = tag_refs[tags.index(start):tags.index(end)+1]

    logging.debug(tags_range)

    return tags_range


def get_tag_messages(tags_range, log_info):
    """
    Add tag messages, commit objects and update the max author length in log_info

    Args:
        tags_range: Range of tags to get information from
        log_info: dictionary containing log information from commits

    Raises:
        ValueError: Can't find tag info

    Returns:
        dictionary containing log info for tags

    """
    for tag in tags_range:
        # Find where info is stored (depends on whether annotated or lightweight tag)
        if hasattr(tag.object, 'author'):
            tag_info = tag.object
        elif hasattr(tag.object.object, 'author'):
            tag_info = tag.object.object
        else:
            raise ValueError("Can't find tag info")

        sha = tag.object.hexsha[:7]
        author = tag_info.author.name
        time_stamp = tag_info.committed_date
        summary = tag_info.summary.replace('\n', ' ')
        # Summary is included in message, so just get extra part
        message = tag_info.message[len(summary):].replace('\n', ' ')
        summary += ' (' + tag.name + ')'

        formatted_time = convert_time_stamp(time_stamp)

        log_info['logs'].append([time_stamp, sha, author, summary, formatted_time, message])

        # Add to dictionary of commit objects for creating diff info later
        log_info['commit_objects'][sha] = tag.commit

        # Find longest author name to pad all lines to the same length
        if len(author) > log_info['max_author_length']:
            log_info['max_author_length'] = len(author)

    return log_info


def convert_time_stamp(time_stamp):

    if isinstance(time_stamp, int):
        ti = time.localtime(time_stamp)
        if len(ti) > 5:
            formatted_time = '{:0>2}'.format(ti[2]) + '/' + '{:0>2}'.format(ti[1]) + '/' + str(ti[0]) + ' ' + \
                             '{:0>2}'.format(ti[3]) + ':' + '{:0>2}'.format(ti[4]) + ':' + '{:0>2}'.format(ti[5])
        else:
            formatted_time = 'no time/date'
    else:
        formatted_time = 'no time/date'

    return formatted_time


def format_log_messages(log_info, raw, verbose):
    """
    Take a dictionary containing log information, convert commit_objects into diff info (if verbose) and
    format into a list of strings; one for each log entry

    Args:
        log_info: dictionary containing log information from commits
        raw: a bool for whether to format in raw or in colour
        verbose: a bool to add extra information (time, date, message body and diff info)

    Returns:
        a list of strings, each string containing a log entry
    """

    blue = 34
    cyan = 36
    green = 32

    logs = log_info['logs']
    commit_objects = log_info['commit_objects']
    max_author_length = log_info['max_author_length']

    # Add formatting parameters
    screen_width = 100
    if verbose:
        # len("e38e73a 01/05/2015 17:20:46 " + ": ") = 30
        overflow_message_padding = max_author_length + 30
    else:
        # len("e38e73a " + ": ") = 10
        overflow_message_padding = max_author_length + 10

    max_line_length = screen_width - overflow_message_padding

    formatted_logs = []
    prev_sha = ''
    for log_entry in logs:

        if len(log_entry) > 1:
            commit_sha = log_entry[1][:7]
        else:
            commit_sha = 'no sha'

        if len(log_entry) > 2:
            name = '{:<{}}'.format(log_entry[2], max_author_length)
        else:
            name = 'no name'

        # Add commit subject summary
        if len(log_entry) > 3:
            commit_message = format_message_width(log_entry[3], max_line_length)
            formatted_message = commit_message[0]
            for line in commit_message[1:]:
                formatted_message += '\n' + '{:<{}}'.format('...', overflow_message_padding) + line
        else:
            formatted_message = '\n'

        # If verbose add date, time, message body and diff info, then add to logs
        if verbose:
            if len(log_entry) > 4:
                date_and_time = log_entry[4]
            else:
                date_and_time = 'no date/time'

            # Check if there is a commit body and append it
            if len(log_entry) > 5 and log_entry[5].strip():
                commit_body = format_message_width(log_entry[5].strip(), max_line_length)
                for line in commit_body:
                    formatted_message += '\n' + '{:<{}}'.format('...', overflow_message_padding) + line

            # Get diff information for commit
            diff_info = ''
            if prev_sha:
                # Pass commit objects corresponding to current and previous commit_sha to get_file_changes
                changed_files = get_file_changes(commit_objects[prev_sha], commit_objects[commit_sha])
                if changed_files:
                    diff_info = "\n\nChanges:\n"
                    for file_change in changed_files:
                        diff_info += file_change
            prev_sha = commit_sha

            formatted_logs.append(colour(commit_sha, blue, raw) + ' ' + colour(date_and_time, cyan, raw) + ' ' +
                                  colour(name, green, raw) + ': ' + formatted_message + diff_info)
        # Otherwise, add to logs
        else:
            formatted_logs.append(colour(commit_sha, blue, raw) + ' ' +
                                  colour(name, green, raw) + ': ' + formatted_message)

    formatted_logs.reverse()

    return formatted_logs


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


def get_file_changes(commit, prev_commit):
    """
    Perform a diff object between two commit objects and extract the changed files from it

    Args:
        commit: Commit object for commit with file changes
        prev_commit: Commit object to compare against

    Returns:
        A list of the changed files between he two commits
    """

    changed_files = []
    for diff in commit.diff(prev_commit):
        # b_blob corresponds to commit and a_blob to prev_commit
        if diff.b_blob:
            if diff.new_file:
                changed_files.append('A     ' + diff.b_blob.path)

                if diff.renamed:
                    changed_files[-1] += ' (Renamed)\n'
                else:
                    changed_files[-1] += '\n'
            else:
                changed_files.append('M     ' + diff.b_blob.path + '\n')

        if diff.a_blob and diff.deleted_file:
            changed_files.append('D     ' + diff.a_blob.path)

            if diff.renamed:
                changed_files[-1] += ' (Renamed)\n'
            else:
                changed_files[-1] += '\n'

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

    raw = set_raw_argument(args.raw)
    pathf.check_technical_area_valid(args.area, args.module_name)
    check_parsed_args_compatible(args.releases, args.earlier_release, args.later_release, parser)
    check_releases_valid(args.releases, parser)

    source = pathf.devModule(args.module_name, args.area)
    if vcs_git.is_repo_path(source):
        repo = vcs_git.temp_clone(source)
        releases = create_release_list(repo)
        logging.debug(releases)
    else:
        raise Exception("Module " + args.module_name + " doesn't exist in " + source)

    # Set start and end releases and check they exist, set to defaults if not given
    start, end = set_log_range(args.module_name, args.releases, args.earlier_release, args.later_release, releases)

    # Create log info from log messages
    # log_info is a dictionary in the form {logs(list), commit_objects(dict), max_author_length(int)}
    log_info = get_log_messages(repo, start, end)

    # Append tag info to log info from tag messages
    tags = get_tags_list(repo, start, end, releases[-1])
    log_info = get_tag_messages(tags, log_info)

    # Check if there are any logs, exit if not
    if not log_info['logs']:
        print("No logs for " + args.module_name + " between releases " +
              args.earlier_release + " and " + args.later_release)
        return 0

    # Sort tags and commits chronologically by the UNIX time stamp in index 0
    log_info['logs'] = sorted(log_info['logs'], key=itemgetter(0))

    # Make list of printable log entries
    formatted_logs = format_log_messages(log_info, raw, args.verbose)

    for log in formatted_logs:
        print(log)

    shutil.rmtree(repo.working_tree_dir)


if __name__ == "__main__":
    sys.exit(main())
