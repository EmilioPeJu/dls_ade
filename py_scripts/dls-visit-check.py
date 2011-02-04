#!/bin/env python2.6
usage = """%prog [options] <beamline>...

This command is checks the Linux LDAP groups against the user office
database and prints out any discrepencies either in LDIF or text
format. if <beamline> is ommitted then all beamlines are processed"""

import sys

def visit_check(start,end,exclude,restore,ldif,args ):
    from dls_scripts.dlsgroups import visit,ldapgrp
    import datetime
    import optparse

    visit=visit()
    group=ldapgrp()
    group.initgid(100000)

    excludedate=datetime.date.today()-datetime.timedelta(exclude)
    startdate=datetime.date.today()-datetime.timedelta(start)
    enddate  =datetime.date.today()+datetime.timedelta(end)

    for name in visit.all():

        if (visit.enddate(name)   and
            visit.startdate(name) and
            ( start and (startdate < visit.enddate(name)) ) and
            ( end and (enddate > visit.startdate(name)) ) and
            args and visit.beamline(name) in args ):

            group_name=name.replace("-","_")
            if group_name not in group.all():
                group_members = set()
                if not ldif:
                    print "Visit",name,"does not have a group (yet). Start:",
                    print visit.startdate(name)
            else:
                group_members = group.members(group_name)

            if (exclude and
                excludedate > visit.enddate(name) and
                group_name not in restore and
                visit.beamline(name) not in restore ):
                
                visit_members = set()
            else:
                bl_staff = group.members(visit.beamline(group_name)+"_staff")
                visit_members = visit.members(name) - bl_staff

            if ldif:
                if visit_members != group_members:
                    group.setmembers( group_name, visit_members )
            else:
                not_in_visit = group_members - visit_members
                if not_in_visit:
                    print "Visit",name,
                    print " is missing all FedId's in the",not_in_visit,
                    print "Start:",visit.startdate(name),
                    print "End:",visit.enddate(name)

                not_in_group = visit_members - group_members
                if not_in_group:
                    print "Group ",group_name,
                    print "is missing all FedId's in the", not_in_group,
                    print "Start:",visit.startdate(name),
                    print "End:",visit.enddate(name)


if __name__ == "__main__":
    from optparse import OptionParser
   
    parser = OptionParser(usage=usage)
    parser.add_option("-f", "--from", dest="start",type="int",default=0,
                      help="Include only visits that ended after <from> days ago")
    parser.add_option("-t", "--to", dest="end",type="int",default=0,
                      help="Include only visits that start before <to> days time")
    parser.add_option("-x", "--exclude", dest="exclude",type="int",default=0,
                      help="Exclude users from groups whose visits ended over <exclude> days ago")
    parser.add_option("-i","--restore-file", dest="restorefile",type="str",nargs=1,
                      help="Filename containing a list of beamlines and visits to restore all users to" )
    parser.add_option("-l", "--ldif", dest="ldif",nargs=0,
                      help="generate difference in ldif format")
    
    (options, args) = parser.parse_args()

    restore=set([])
    if options.restorefile != None:
        try:
            for line in file( options.restorefile ):
                restore |= set( line.split())
        except:
            print >> sys.stderr, "Cannot open restore file:",options.restorefile
            sys.exit(1)

    sys.exit(visit_check(options.start, options.end,options.exclude,restore,options.ldif!=None,args))
