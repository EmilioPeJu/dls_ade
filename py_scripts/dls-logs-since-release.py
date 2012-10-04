#!/bin/env dls-python2.6
# This script comes from the dls_scripts python module

usage = """%prog [options] [<module_name> [<earlier_release> [<later_release>]]]

Default <area> is 'support'.
Print all the log messages for module <module_name> in the <area> area of svn
from one the revision number when <earlier_release> was done, to the revision
when <later_release> was done. If not specified, <earlier_release> defaults to
revision 0, and <later_release> defaults to the head revision. If
<earlier_release> is given an invalid value (like 'latest') if will be set
to the latest release."""

import os, sys, time

BLACK   = 30
RED     = 31
GREEN   = 32
YELLOW  = 33
BLUE    = 34
MAGENTA = 35
CYAN    = 36
GREY    = 37

raw = False
def colour(word, col):
    if raw:
        return word
    esc = 27
    return '%(esc)c[%(col)dm%(word)s%(esc)c[0m' % locals()

def logs_since_release():
    from dls_scripts.options import OptionParser
    parser = OptionParser(usage)
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose",\
                    help="Print lots of log information")
    parser.add_option("-r", "--raw", action="store_true", dest="raw",\
                    help="Print raw text (not in colour)")
                    
    (options, args) = parser.parse_args()

    if len(args) not in range(4):
        parser.error("Incorrect number of arguments.")
        
    # setup the environment
    from dls_environment import environment    
    e = environment()
    
    # import svn client
    from dls_scripts.svn import svnClient    
    svn = svnClient()

    # show modified files if verbose    
    if options.verbose:
        verbose = True
    else:
        verbose = False

    # don't write coloured text if options.raw (it confuses less)
    if  not options.raw and ( not sys.stdout.isatty() or 
                              os.getenv("TERM") == None  
                              or "dumb" == os.getenv("TERM") ):
        global raw
        raw = True
        
    # if module specified then check logs for that module        
    if args:    
        module = args[0]
        # check that iocs have a technical area
        if options.area == "ioc":
            assert len(module.split('/'))>1, 'Missing Technical Area under Beamline'        
        source = svn.devModule(module,options.area)
        release = svn.prodModule(module,options.area)
    # otherwise do it for the entire area        
    else:
        module = options.area
        source = svn.devArea(options.area)
        release = svn.prodArea(options.area)        
    
    # Work out the initial and end release numbers
    start = svn.Revision(svn.opt_revision_kind.number,0)
    end = svn.Revision(svn.opt_revision_kind.head)    
                
    # Check for existence of this module in various places in the repository
    # and note revisions
    assert svn.pathcheck(source), 'Repository does not contain "'+source+'"'
    
    if svn.pathcheck(release):
        release_dir = release.replace(svn.info2(release, recurse = False)[0][1]["repos_root_URL"], "")    
                          
        # Now grab the logs from the release dir
        r_logs = svn.log(release, discover_changed_paths = True)

        if len(args) > 1:
            early_num = args[1]   
            releases = []    
            # Create a list of release numbers and their created dates
            for log in r_logs:
                if log["changed_paths"]:
                    for pdict in log["changed_paths"]:
                        if pdict["action"].upper() == "A":
                            rnum = pdict["path"].replace(release_dir, "").lstrip("/")
                            if rnum and "/" not in rnum and pdict["copyfrom_revision"]:
                                releases = [(r,l) for r,l in releases if r != rnum] + [(rnum, pdict["copyfrom_revision"])]
            # Sort them by rev
            releases = [(r, l) for _, r, l in sorted([(l.number, r, l) for r, l in releases])]
            
            # adjust the start rev to be early_release
            i = 0
            while i < len(releases) and releases[i][0] != early_num:
                i += 1
            if i == len(releases):
                i = -1
                print 'Repository does not contain "%s", using latest release "%s"'%(early_num, releases[-1][0])
            start = releases[i][1]
            if len(args) > 2:
                late_num = args[2]
                j = len(releases) - 1
                while j > 0 and releases[j][0] != late_num:
                    j -= 1
                if j == 0:
                    print 'Repository does not contain "%s", using head'%(late_num)
                else:
                    end = svn.Revision(svn.opt_revision_kind.number,releases[j][1].number + 1)
            r_logs = svn.log(release, revision_start = start, revision_end = end,\
                     discover_changed_paths = True)                        
    else:
        r_logs = []                    
    
    # now grab the logs from the 2 dirs
    logs =   svn.log(source, revision_start = start, revision_end = end,\
                     discover_changed_paths = verbose)    

    for l in r_logs:
        l["message"] += " (Release dir %s)" % l["changed_paths"][0]["path"].replace(release_dir, "").lstrip("/")
        if l["changed_paths"][0]["copyfrom_revision"]:
            # hack the revision so it's a little later than the copy from location
            class rev:
                number = l["changed_paths"][0]["copyfrom_revision"].number + 0.1            
            l["revision"] = rev()
    
    # intersperse them
    ll =  [(l["revision"].number, l) for l in r_logs]                                                          
    ll += [(l["revision"].number, l) for l in logs if l["revision"].number > start.number]    
    logs = [l[1] for l in reversed(sorted(ll))]

    # Now print them
    print "Log Messages:"    
    for log in logs:
        mess = log["message"].split(module+":",1)
        if len(mess)==1:
            mess = mess[0].strip()
        else:
            mess = mess[1].strip()
        rev = "(r%s)"%int(log["revision"].number)
        pre = ("%%-%ds %%s:" % (17 - len(rev))) % (log["author"], rev)
        if verbose:                                
            header = "%s %s"%(pre,time.ctime(log["date"]))
            print colour(header, RED)
            print colour("-"*min(80,len(header)), RED)
            print mess
            if log["changed_paths"]:
                print "Changes:"
                for change in log["changed_paths"]:
                    print "  %s %s"%(change["action"],change["path"])
                print
            print
        else:
            print "%s %s"%(colour(pre, RED), mess)
                              
if __name__ == "__main__":
    import sys
    sys.path.append("..")
    sys.exit(logs_since_release())
