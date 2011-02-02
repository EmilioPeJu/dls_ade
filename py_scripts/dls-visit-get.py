#!/bin/env dls-python

usage = """%prog [options] <fedid>...

This command is similar to the Linux 'groups' command except it lists
the visits for the current or specified user, rather than the Linux
groups. Of course, there is a lot of overlap between these for
beamline scientists.

The default <fedid> is the current user."""

import sys

def visit_get(args):
    from dls_scripts.dlsgroups import visit

    if len(args) == 0:
        usernames = [ getpass.getuser() ]
    else:
        usernames=args

    for user in usernames:
        visit=visit(user)

        if len(args) > 0:
            print user,':',
        
        for group in visit.all():
            print group,

        print

if __name__ == "__main__":
    from optparse import OptionParser

    parser = OptionParser(usage=usage)
    (options, args) = parser.parse_args()

    sys.exit(visit_get(args))
