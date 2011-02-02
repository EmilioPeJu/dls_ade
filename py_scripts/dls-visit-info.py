#!/bin/env python2.6
usage = """%prog [options] <visit>...

This command is similar to the Linux 'getent group' command except it
lists the visits for the information about the specified visit, rather
than the Linux groups. Of course, there is a lot of overlap between
these for beamline scientists. The result is a colon delimited line
per visit. The fields are:

<visit>:<beamline>:<start-date>:<end-date>:<staff?>: <fedid1> ...

If no visit is specified all visits are returned."""

import sys

def visit_info(fullname,names):
    """Command similar to Linux getent group command to return information about visits, and users in a visit"""
    from dls_scripts.dlsgroups import visit
    import getpass
    import pwd
   
    visit=visit()

    if len(names) == 0:
        visits=visit.all();
    else:
        visits = []

        for name in names:
            if name.replace("-","_") not in visit.all():
                print name, "is not a valid visit"
            else:
                visits.append(name)

            if len(visits) == 0:
                sys.exit(1)

    for raw_name in visits:
        name=raw_name.replace("-","_")

        try:
            print "%s:%s:%s:%s:%s:" % (raw_name,
                                       visit.beamline(name),
                                       visit.startdate(name).strftime("%d-%b-%Y"),
                                       visit.enddate(name).strftime("%d-%b-%Y"),
                                       "staff" if visit.is_staff(name) else "non-staff" ),
        except:
            print "%s::::" % (name),

        if fullname:
            print
            for user in visit.members(name):
                print "   -",pwd.getpwnam(user)[4]

        else:
            for user in visit.members(name):
                print user,
        
            print

if __name__ == "__main__":
    from optparse import OptionParser
   
    parser = OptionParser(usage=usage)
    parser.add_option("-f", "--full-name", dest="fullname", nargs=0,
                      help="Display full name of user, not just username (FedID)")
    (options, args) = parser.parse_args()

    sys.exit(visit_info(options.fullname!=None,args))
