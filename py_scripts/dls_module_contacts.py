#!/bin/env dls-python
# This script comes from the dls_scripts python module

usage = """%prog [options] [<module_name_1> [<module_name_2> [...]]]

Default <area> is 'support'.
Utility for setting and showing primary contact (contact) and seconday contact
(cc) properties. If any <module_name_N> are specified, only show and set
properties on those modules, otherwise operate on the entire area.

e.g.
%prog ip autosave calc
# View the contacts for the ip, autosave and calc modules

%prog -a support -s
# View all the module contacts and ccs in the support area in csv format

%prog -c tmc43 -d jr76 -p pysvn
# Set the python module pysvn to have contact tmc43 and cc jr76

%prog -m /tmp/module_contacts_backup.csv
# Import the module contacts and cc from the csv file and set them in svn.
# The csv file is the same format as produced by the -s command, but
# any specified contact and cc names are ignored, only fed-ids are used."""

import os, sys, csv
from dls_environment.options import OptionParser
from dls_environment.svn import svnClient, pysvn
users = {}
svn = svnClient()
import pysvn

def lookup(uid):
    # ldap lookup using the commandline interface (takes a while)
    if not users.has_key(uid):
        cmd = os.popen("ldapsearch -x -d ldap.diamond.ac.uk uid="+\
                       uid+" 2> /dev/null | grep gecos")
        lines = cmd.readlines()
        if lines:
            users[uid] = lines[0].replace("gecos:","").strip()
        else:
            cmd = os.popen('ypcat -k passwd | grep "%s %s:"'%(uid,uid))
            lines = cmd.readlines()
            if lines and len(lines[0].split(":"))>4:
                users[uid] = lines[0].split(":")[4]
            else:
                users[uid] = uid
    return users[uid]

def lookup_contacts(module,area):
    path = svn.devModule(module,area)
    contact = svn.propget("dls:contact",path)
    if contact:
        contact = contact.values()[0]
    else:
        contact = ""
    cc = svn.propget("dls:cc",path)     
    if cc:
        cc = cc.values()[0]
    else:
        cc = ""
    return (contact.strip(),cc.strip())

def module_contacts():    
    parser = OptionParser(usage)
    parser.add_option("-c","--contact",action="store",type="string",\
                      metavar="FED_ID",dest="contact",\
                      help="Set the contact property to FED_ID")
    parser.add_option("-d","--cc",action="store",type="string",\
                      metavar="FED_ID",dest="cc",\
                      help="Set the cc property to FED_ID")
    parser.add_option("-s", "--csv", action="store_true", dest="csv",\
                      help="Print output as csv file")
    parser.add_option("-m", "--import", action="store",type="string",\
                      metavar="CSV_FILE",dest="imp",\
                      help="Import a CSV_FILE with header and rows of format:"+\
                      "\nModule,Contact,Contact Name,CC,CC Name")

    (options, args) = parser.parse_args()

    if options.imp and (options.cc or options.contact):
        parser.error("Option --import cannot be used with --contact or --cc")

    # setup the environment
    modules = []

    # create the dict of modules
    if args:
        for arg in args:
            modules.append(arg)
    else:
        if not options.csv:
            print "Building list of modules..."
        path = svn.devArea(options.area)
        if options.area == "ioc":
            for l in [ l for l in svn.list(path, depth=pysvn.depth.immediates) if l[0]["path"]!=path ]:
                lname = l[0]["path"]
                mods = svn.list(lname, depth=pysvn.depth.immediates)
                # if an IOC has a configure directory, there are no TAs listed here
                if "configure" in [ s[0]["path"][-9:] for s in mods ]:
                    modules.append(lname.split("/")[-1])
                else:
                    for m in [ m for m in mods if m[0]["kind"]==pysvn.node_kind.dir and m[0]["path"]!=lname]:
                        split = m[0]["path"].split("/")
                        # add each of the TAs
                        modules.append(split[-2]+"/"+split[-1])
        else:
            for l in [ l for l in svn.list(path, depth=pysvn.depth.immediates) if l[0]["path"]!=path ]:
                modules.append(l[0]["path"].split("/")[-1])

    # print them and finish here if we don't have to set them
    if not (options.contact or options.cc or options.imp):
        if options.csv:
            print "Module,Contact,Contact Name,CC,CC Name"
        for name in modules:
            contact,cc = lookup_contacts(name,options.area)
            if options.csv:
                print "%s,%s,%s,%s,%s"%(name,contact,lookup(contact),\
                                        cc,lookup(cc))
            else:
                out = name + ": "
                if contact:
                    out += "Contact is %s (%s)" % (lookup(contact), contact)
                if cc:
                    out += "; cc is %s (%s)" % (lookup(cc), cc)
                if not contact and not cc:
                    out += "No contacts set"
                print out
        sys.exit()

    # give user a chance to back out
    if len(args) == 0 and (options.contact or options.cc):
        a = ""
        while not a.upper() in ["Y","N"]:
            a=raw_input("Are you sure you want to set the contacts and cc for"+\
                        " all modules in area %s? Enter Y or N: " % options.area)
        if a.upper() == "N":
            sys.exit()

    contacts = []
    # import contact list from a csv file
    if options.imp:
        reader = csv.reader(open(options.imp,"rb"))
        for row in reader:
            if len(row)>1 and row[0]!="Module":
                module = row[0].strip()
                contact = row[1].strip()
                if len(row)>3:
                    cc = row[3].strip()
                else:
                    cc = ""
                assert module in modules, "Module %s not in %s"%(module,modules.keys())
                assert module not in [x[0] for x in contacts], "Module %s defined twice"%module
                contacts.append((module,contact,cc))
    else:
        for module in modules:
            contacts.append((module,options.contact,options.cc))


    # checkout modules and change properties
    chk_dir = "/tmp/module_contacts_change"
    os.system("rm -rf " + chk_dir)
    for module, contact, cc in contacts:
        svn.checkout(svn.devModule(module, options.area), chk_dir, recurse=False)
        contact = contact.strip() if contact is not None else None
        cc = cc.strip() if cc is not None else None
        msg = module + ": changed module contacts: "
        if contact is not None:
            print "%s: Setting contact to %s (%s)" % (module, lookup(contact), contact)
            msg += "Set contact to %s (%s). " % (lookup(contact), contact)
            svn.propset("dls:contact", contact, chk_dir)
        if cc is not None:
            print "%s: Setting cc to %s (%s)" % (module, lookup(cc), cc)
            msg += "Set cc to %s (%s). " % (lookup(cc), cc)
            svn.propset("dls:cc", cc, chk_dir)
        svn.checkin(chk_dir, msg)
        os.system("rm -rf " + chk_dir)

if __name__=="__main__":
    sys.exit(module_contacts())
