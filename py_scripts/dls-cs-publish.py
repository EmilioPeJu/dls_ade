#!/bin/env dls-python
# This script comes from the dls_scripts python module

usage = """%prog [options] <module> <release>

Default <area> is 'support'.
Publish a module <module> in the <area> area of the repository to the downloads
page. The script takes the following steps:
* svn export of the release
* copy built documentation or docs directory in and remove .svn dirs
* remove documentation/private and docs/private directories
* make a web release in /dls_sw/cs-publish/<area>/<module>/<release
* copy the documentation into the web release directory
* zip up the export and copy it into the web release directory
* regenerate an index page from all the releases in the directory

Note: if you are publishing a new module and not just a new release of an
existing one, then you need to edit /dls_sw/cs-publish/<area>/index.html, 
placing a new link and description in the table of modules."""

import os, sys
from dls_scripts.svn import svnClient
from dls_scripts.options import OptionParser
from dls_environment import environment

def cs_publish():
    parser = OptionParser(usage)
    parser.add_option("-f", "--force",
        action="store_true", dest="force",
        help="force the publish, disable warnings")    
    (options, args) = parser.parse_args()
    
    if len(args)!=2:
        parser.error("Incorrect number of arguments.")
    module = args[0]
    release = args[1]
    area = options.area

    # setup the environment
    path = "/tmp"
    docdirs = ["documentation","docs"]

    # find the released svn directory    
    svn = svnClient()
    if options.area == "ioc" and a.upper()!="Y":
        assert len(module.split('/'))>1, \
            'Missing Technical Area under Beamline'
    source = svn.prodModule(module,options.area)

    # Check for existence of this module in various places in the repository
    assert svn.pathcheck(source), \
        'Repository does not contain the "'+source+'" module'

    # Export to filesystem
    export = path+"/"+module+"-"+release    
    print 'Exporting to '+export+'...'
    if os.path.exists(export):
        os.system("rm -rf %(export)s"%locals())
    svn.export(source+"/"+release, export)

    # Locate built version of module
    e = environment()    
    prodPath = e.prodArea(options.area) + "/" + module + "/" + release
    
    # Check the release isn't on the webserver
    webPath = "/dls_sw/cs-publish/%(area)s/%(module)s"%locals() 
    if os.path.isdir(webPath+"/"+release):
        msg = "%(module)s release %(release)s already exists on webserver" % \
            locals()
        if options.force:
            print "Warning: "+msg+". Overwriting"
            os.system("rm -rf %(webPath)s/%(release)s"%locals())
        else:
            raise AssertionError, msg
    os.makedirs(webPath+"/"+release)    
    
    # replace documentation with built version
    for docdir in docdirs:
        if os.path.exists(export+"/"+docdir):
            os.system("rm -rf %(export)s/%(docdir)s"%locals())
            os.system("cp -rf %(prodPath)s/%(docdir)s %(export)s/%(docdir)s"%locals())
            os.system(r"find %(export)s/%(docdir)s -name '.svn' -prune -exec rm -rf {} \;"%locals())
            # do we want to remove the docdir makefile?
#            os.system("rm -rf %(export)s/%(docdir)s/Makefile"%locals())
            os.system("rm -rf %(export)s/%(docdir)s/private"%locals())
            os.system("chmod -R ug+rwX,o+rX,o-w %(export)s"%locals())            
            os.system("cp -rf %(export)s/%(docdir)s %(webPath)s/%(release)s/%(docdir)s"%locals())        
            
    # python files need the correct versioned setup.py
    if options.area == "python":
        os.system("cp -f %(prodPath)s/setup.py %(export)s"%locals())
          
    # Zip up
    tgz = "%(path)s/%(module)s-%(release)s.tgz"%locals()
    print 'Zipping up...'
    os.system("tar -czf %(tgz)s -C %(path)s %(module)s-%(release)s"%locals())
    
    # put it on the webserver
    print 'Copying to '+webPath +'...'
    os.system("cp %(tgz)s %(webPath)s/%(release)s"%locals())

    # regenerate the webpage
    print 'Generating index page...'
    if not os.path.isfile(webPath+"/style_right.css"):
        os.system("cp %s/../style_right.css %s/style_right.css"%(webPath,webPath))
    releases = e.sortReleases([x
        for x in os.listdir(webPath)
        if os.path.isdir(webPath+"/"+x) ])
    releases.reverse()
    text = """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<HTML lang="en">

<HEAD>
  <META http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
  <TITLE>Releases of %(module)s</TITLE>
  <LINK href="style_right.css" rel="stylesheet" type="text/css">
</HEAD>

<BODY>

<HR align=left size=4 noshade width="100%%">
   <H1>Releases of %(module)s</H1>
<HR align=left size=4 noshade width="100%%">

<P>This page lists the available releases of %(module)s</P>

<TABLE width="100%%" border="0" align="center" cellpadding="12" cellspacing="2">
 <THEAD>
  <TR class="title">
   <TH>Name</TH> <TH>Link</TH> <TH>Documentation</TH>
  </TR>
 </THEAD>
 <TBODY>
"""%locals()

    for release in releases:
        text += '  <TR class="releases">\n'
        text += '   <TD>%(release)s</TD>\n'%locals()
        filename = "%(module)s-%(release)s.tgz"%locals()
        text += '   <TD><a href=%(release)s/%(filename)s>%(filename)s</a></TD>\n'%locals()  
        text += '   <TD>'
        htmls = []
        pdfs = []
        for docdir in docdirs:
            if os.path.isdir("%(webPath)s/%(release)s/%(docdir)s/html"%locals()):
                docpath = docdir + "/html"
            elif os.path.isdir("%(webPath)s/%(release)s/%(docdir)s"%locals()):
                docpath = docdir
            else:
                continue
            htmls = [ x.replace(".html","") for x in os.listdir("%(webPath)s/%(release)s/%(docpath)s"%locals()) if x.endswith(".html") ]            
            pdfs = [ x for x in os.listdir("%(webPath)s/%(release)s/%(docpath)s"%locals()) if x.endswith(".pdf") ]                        
        if htmls:
            # if an index exists, only include that
            if "index" in htmls:
                htmls = ["index"]
            for html in htmls:
                text += '<a href=%(release)s/%(docpath)s/%(html)s.html target="_top">%(html)s</a></TD>\n'%locals() 
        elif pdfs:
            for pdf in pdfs:
                text += '<a href=%(release)s/%(docpath)s/%(pdf)s target="_top">%(pdf)s</a></TD>\n'%locals()             
        else:
            text += "None"
        text += '</TD>\n'            
        text += "  </TR>\n"
        
    text += "</TABLE>\n</BODY>\n</HTML>\n"
    
    open(webPath+"/index.html","w").write(text)   
    
    # clean up
    print "Cleaning up..."
    os.system("rm %(tgz)s"%locals())
    os.system("rm -rf %(path)s/%(module)s-%(release)s"%locals())
    print 'Done'
    
if __name__ == "__main__":
    sys.exit(cs_publish())
