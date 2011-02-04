#!/bin/env python2.6
usage = """%prog [options] <beamline>...

This command is checks the Linux LDAP groups against the user office
database and prints out any discrepencies either in LDIF or text
format."""

import sys

def visit_check(start,end,exclude,ldif, restore ):
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
            ( end and (enddate > visit.startdate(name)) )):

            group_name=name.replace("-","_")
            if group_name not in group.all():
                group_members = set()
                if not ldif:
                    print "Visit",name,"does not have a group (yet). Start:",
                    print visit.startdate(name)
            else:
                group_members = group.members(group_name)

            if (exclude and
                group_name not in restore and
                excludedate > visit.enddate(name)):
                
                visit_members = set()
            else:
                visit_members = visit.members(name)

            excess_members= group_members ^ visit_members                   
            not_in_visit = excess_members & group_members
            not_in_group = excess_members & visit_members

            if ldif:
                if not_in_group or not_in_visit:
                    group.setmembers( group_name, not_in_group, not_in_visit )
            else:
                if not_in_visit:
                    print "Visit",name,
                    print " is missing all FedId's in the",not_in_visit,
                    print "Start:",visit.startdate(name),
                    print "End:",visit.enddate(name)

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
    parser.add_option("-r", "--restore", dest="restore",type="string",nargs=1,
                      help="Restore all users to the specified visits")    
    parser.add_option("-l", "--ldif", dest="ldif",nargs=0,
                      help="generate difference in ldif format")
    
    (options, args) = parser.parse_args()

    sys.exit(visit_check(options.start, options.end,options.exclude,options.ldif!=None,args))
