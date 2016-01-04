#!/bin/env dls-python
# This script comes from the dls_scripts python module

import os
import sys
import logging
from argument_parser import ArgParser
from dls_environment import environment
import path_functions as path
import vcs_git
from pkg_resources import require
require('GitPython')
import git

e = environment()
logging.basicConfig(level=logging.WARNING)

usage = """
Default <area> is 'support'.
Check if a module in the <area> area of the repository has had changes committed since its last release.
"""

BLUE = 34
GREEN = 32


def make_parser():

    parser = ArgParser(usage)
    parser.add_argument("module_name", type=str, help="name of module to release")
    return parser


def check_technical_area_valid(args, parser):

    if args.area == "ioc" and not len(args.module.split('/')) > 1:
        parser.error("Missing Technical Area Under Beamline")


def colour(word, col):
    # >>> I have just hard coded the char conversion of %27c in, as I couldn't find the
    # .format equivalent of %c, is anything wrong with this?
    return '\x1b[{col}m{word}\x1b[0m'.format(col=col, word=word)


def format_message_width(message, line_len):

    if not isinstance(message, list):
        message = [message]
    for i, part in enumerate(message):
        if len(message[i]) > line_len:
            # Find first ' ' before line_len cut-off
            line_end = line_len - message[i][line_len::-1].find(' ')
            # Append second section to separate list entry
            if ' ' in message[i][line_len::-1]:
                # +1 -> without ' '
                message.insert(i+1, message[i][line_end+1:])
            else:
                # Keep string as is if there are no spaces (e.g. long file paths)
                message.insert(i+1, message[i][line_end:])
            # Keep section before cut-off
            message[i] = message[i][:line_end]

    return message


def main():

    parser = make_parser()
    args = parser.parse_args()

    check_technical_area_valid(args, parser)

    module = args.module_name
    source = path.devModule(module, args.area)
    logging.debug(source)

    # Check for existence of this module in various places in the repository and note revisions
    if not vcs_git.is_repo_path(source):
        parser.error("Repository does not contain " + source)

    if vcs_git.is_repo_path(source):
        if os.path.isdir('./' + module):
            repo = vcs_git.git.Repo(module)
            releases = vcs_git.list_module_releases(repo)
        else:
            vcs_git.clone(source, module)
            repo = vcs_git.git.Repo(module)
            releases = vcs_git.list_module_releases(repo)

        last_release_num = releases[-1]
    else:
        parser.error(source + "does not exist on the repository.")
        # return so 'releases' can't be referenced before assignment
        return 1

    if len(releases) == 0:
        print(module + " (No release done): Outstanding changes.")
        return

    logs = repo.git.log(last_release_num + "..HEAD",
                        "--format=%h %aD %cn %n%s%n%b<END>").split('<END>\n')
    if logs:
        print("Changes have been made to " + module + " since most recent release " + last_release_num + ":\n")
        # formatted_logs = []
        # max_line_length = 80
        # message_padding = 30
        # for entry in logs:
        #     commit_hash = entry.split()[0]
        #     name = '{:<20}'.format(entry.split()[7] + ' ' + entry.split()[8])
        #
        #     # Add commit subject message
        #     commit_message = filter(None, entry.split('\n')[1])
        #     if len(commit_message) > max_line_length:
        #         commit_message = format_message_width(commit_message, max_line_length)
        #         formatted_message = commit_message[0]
        #         for line in commit_message[1:]:
        #             formatted_message += '\n' + '{:<{}}'.format('...', message_padding) + line
        #     else:
        #         formatted_message = commit_message
        #
        #     formatted_logs.append(colour(commit_hash, BLUE) + ' ' +
        #                           colour(name, GREEN) + ': ' + formatted_message)
        #
        # for log in formatted_logs:
        #     print(log)
    else:
        print("No changes made to " + module + " since release " + last_release_num)


if __name__ == "__main__":
    sys.exit(main())
