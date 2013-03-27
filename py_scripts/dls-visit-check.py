#!/bin/env dls-python2.6
usage = """%prog [options] <beamline>...

This command is checks the Linux LDAP groups against the user office
database and prints out any discrepencies either in LDIF or text
format. if <beamline> is ommitted then all beamlines are processed"""

import sys

debug=False

def visit_check(start,end,staff_end,exclude,restore,ldif,dir,userlist,visit_list,args ):
    from dls_scripts.dlsgroups import visit,ldapgrp
    import datetime
    import optparse

    visit=visit()
    group=ldapgrp()
    group.initgid(100000)

    fedids = set()

    dls_dasc = group.members("dls_dasc")

    excludedate=datetime.date.today()-datetime.timedelta(exclude)
    startdate=datetime.date.today()-datetime.timedelta(start)
    enddate  =datetime.date.today()+datetime.timedelta(end)
    bl_staff_removal_date = datetime.date.today()-datetime.timedelta(staff_end)

    for name in visit.all():

        if (visit.enddate(name)   and
            visit.startdate(name) and
            not (start and (visit.enddate(name) <= startdate) ) and
            not (end   and (visit.startdate(name) >= enddate) ) and
            not (args  and visit.beamline(name) not in args) ):

            if visit_list:
                print name
                continue

            group_name=name.replace("-","_")
            if group_name not in group.all():
                group_members = set()
                if (not ldif and not dir and not userlist):
                    print "Visit",name,"does not have a group (yet). Start:",
                    print visit.startdate(name)
            else:
                group_members = group.members(group_name)

            if debug:
                if group_name in restore:
                    print "restoring based on name: %s" % name
                if visit.beamline(name) in restore:
                    print "restoring based on beamline: %s" % name

            if (exclude and
                excludedate > visit.enddate(name) and
                group_name not in restore and
                visit.beamline(name) not in restore ):

                visit_members = set()
            else:
                visit_members = visit.members(name)
                bl_staff = group.members(visit.beamline(group_name)+"_staff")
                if not bl_staff:
                    bl_staff = group.members(visit.beamline(group_name).
                               replace("-1","")+"_staff")
                if bl_staff:
                    visit_members -= bl_staff
                if dls_dasc:
                    visit_members -= dls_dasc

            fedids |= visit_members

            if ldif:
                if ( ( visit_members != group_members )
                        or not visit_members):
                    group.setmembers( group_name, visit_members )
            elif dir:
                # output format will be:
                # don't create line for bl_staff members
                # avoiding special ACLs for bl_staff
                # FEDID,VISITDIR,VISITGROUP,BEAMLINE,YEAR
                visit_members -= bl_staff
                for user in visit_members:
                    print "%s,%s,%s,%s,%s" % ( user,name.replace("_","-"),
                            group_name,visit.beamline(group_name),
                            visit.startdate(group_name).year )
                if not visit_members:
                    print ",%s,%s,%s,%s" % (name.replace("_","-"),
                            group_name,visit.beamline(group_name),
                            visit.startdate(group_name).year )
            elif not userlist:
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

    if userlist:
        dls_staff = group.members("dls_staff")
        fedids -= dls_staff
        # every existing user will have a group with the same name
        # only print users where no group exists as these need to be created
        if fedids:
            for name in fedids:
                usergroup = group.members(name)
                if ( usergroup == None ):
                    print name

if __name__ == "__main__":
    from optparse import OptionParser

    parser = OptionParser(usage=usage)
    parser.add_option("-f", "--from", dest="start",type="int",default=0,
                      help="Include only visits that ended after <from> days ago")
    parser.add_option("-t", "--to", dest="end",type="int",default=0,
                      help="Include only visits that start before <to> days time")
    parser.add_option("-x", "--exclude", dest="exclude",type="int",default=0,
                      help="Exclude users from groups whose visits ended over <exclude> days ago")
    parser.add_option("-s", "--remove_staff_to", dest="remove_staff_end",type="int", default=30,
                      help="Exclude bl-staff from groups that end before <staff_end> days ago")
    parser.add_option("-i","--restore-file", dest="restorefile",type="str",nargs=1,
                      help="Filename containing a list of beamlines and visits to restore all users to" )
    parser.add_option("-l", "--ldif", dest="ldif",nargs=0,
                      help="generate difference in ldif format")
    parser.add_option("-d", "--directories", dest="directory", nargs=0,
                      help="generate list of visits and beamlines to create experiment directories" )
    parser.add_option("-u", "--users", dest="userlist", nargs=0,
                      help="generate list containing all (non-staff) users listed on visits" )
    parser.add_option("-v", "--visits", dest="visitlist", nargs=0,
                      help="generate list containing all visits in the specified interval" )
    parser.add_option("-D", "--debug", dest="debug", nargs=0,
                      help="enable debugging output" )

    (options, args) = parser.parse_args()

    if options.debug != None :
        print "enabling debug"
        debug=True

    restore=set([])
    if options.restorefile != None:
        try:
            for line in file( options.restorefile ):
                if line[:1] != "#":
                    line=line.replace("-","_")
                    restore |= set( line.split())
        except:
            print >> sys.stderr, "Cannot open restore file:",options.restorefile
            sys.exit(1)

        if debug:
            print "restore: %s" % restore

    sys.exit(visit_check(options.start, options.end,options.remove_staff_end,
             options.exclude,restore,options.ldif!=None,options.directory!=None,
             options.userlist!=None,options.visitlist!=None,args))
