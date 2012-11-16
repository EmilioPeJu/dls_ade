#!/bin/env dls-python2.6
usage = """%prog [options]           ...

This command lists the visits on beamlines in beamline and start date
order"""

import sys

def visit_list( start, end, beamline, current, previous ):
    from dls_scripts.dlsgroups import visit,ldapgrp
    import datetime
    import optparse

    print start, end, beamline, current, previous

    visit=visit()

    if not (start is None):
        startdate=datetime.date.today()-datetime.timedelta(start) 
    if (not end is None):
        enddate  =datetime.date.today()+datetime.timedelta(end) 

    last=None
    for name in sorted( sorted(visit.all(), key=lambda k: visit.startdate(k) ),
                        key=lambda k: visit.beamline(k) ):

        if (visit.enddate(name)   and
            visit.startdate(name) and
            ((start is None) or (visit.enddate(name) <= startdate) ) and
            ((end is None)   or (visit.startdate(name) >= enddate) ) and
            ((beamline is None) or (visit.beamline(name) == beamline) )):

            if (current):   
                if ( visit.startdate(name) < datetime.date.today() and
                     datetime.date.today() < visit.enddate(name) ):
                    print visit.beamline(name), name, visit.startdate(name), visit.enddate(name)
            elif (previous):
                if ( last != None and
                     ( visit.enddate(name) > datetime.date.today() or
                       visit.beamline(last) != visit.beamline(name) ) and
                     visit.enddate(last) < datetime.date.today() ):
               
                    print visit.beamline(last), name, visit.startdate(last), visit.enddate(last) 
            else:
                print visit.beamline(name), name, visit.startdate(name), visit.enddate(name) 

        last = name

    if (previous and
        (datetime.date.today() < visit.enddate(last)) and
        ((beamline is None) or visit.beamline(last) == beamline )): 
        print visit.beamline(last), name, visit.startdate(last), visit.enddate(last) 

if __name__ == "__main__":
    from optparse import OptionParser

    parser = OptionParser(usage=usage)
    parser.add_option("-f", "--from", dest="start",type="int",
                      help="Include only visits that ended after <from> days ago")
    parser.add_option("-t", "--to", dest="end",type="int",
                      help="Include only visits that start before <to> days time")
    parser.add_option("-b", "--beamline", dest="beamline",type="str",nargs=1,
                      help="Just print visits for specified beamline")
    parser.add_option("-c", "--current", dest="current", action="store_true",
                      help="Just print current visit" )
    parser.add_option("-p", "--previous", dest="previous", action="store_true",
                      help="Just print previous visit" )

    (options, args) = parser.parse_args()


    sys.exit(visit_list(options.start, options.end, options.beamline, options.current, options.previous))
    
