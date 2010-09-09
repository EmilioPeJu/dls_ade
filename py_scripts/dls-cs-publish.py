#!/bin/env dls-python
# This script comes from the dls_scripts python module

usage = """%prog [options] <module> <release>

Default <area> is 'support'.
Publish a module <module> in the <area> area of the repository to the downloads
page. The script takes the following steps:
* svn export of the release
* copy built documentation or docs directory in and remove .svn dirs
* remove documentation/private and docs/private directories
* make a web release in /dls_sw/cs-publish/<area>/<module>/<release>
* copy the documentation into the web release directory
* copy any builder iocs into the web release directory
* remove the etc directory
* zip up the export and copy it into the web release directory
* regenerate an index page (releases.html) from all the releases in the directory

Note: if you are publishing a new module and not just a new release of an
existing one, then you need to edit /dls_sw/cs-publish/<area>/header.html, 
placing a new link and description in the table of modules."""

import os, sys, shutil

def cs_publish():
    from dls_scripts.options import OptionParser
    parser = OptionParser(usage)
    # setup the environment
    from dls_environment import environment    
    e = environment()    
    epics_version = e.epicsVer()    
    parser.add_option("-f", "--force",
        action="store_true", dest="force",
        help="force the publish, disable warnings")    
    parser.add_option("-e", "--epics_version", action="store", type="string", 
        dest="epics_version", 
        help="Change the epics version. This will determine where the built " \
            "documentation is copied from. Default is %s " \
            "(from your environment)" % e.epicsVer())        
    (options, args) = parser.parse_args()
    
    if len(args)!=2:
        parser.error("Incorrect number of arguments.")
    module = args[0]
    release = args[1]
    area = options.area
    # set epics version, and extension
    if options.epics_version:
        if e.epics_ver_re.match(options.epics_version):
            e.setEpics(options.epics_version)
        else:
            parser.error("Expected epics version like R3.14.8.2, got '%s'" % \
                options.epics_version)
    path = "/tmp"
    docdirs = ["documentation","docs"]    
    
    # import svn client
    from dls_scripts.svn import svnClient    
    svn = svnClient()
    
    if options.area == "ioc" and a.upper()!="Y":
        assert len(module.split('/'))>1, \
            'Missing Technical Area under Beamline'
    source = svn.prodModule(module,options.area)

    # Check for existence of this module in various places in the repository
    assert svn.pathcheck(source), \
        'Repository does not contain the "'+source+'" module'

    # Locate built version of module
    prodPath = e.prodArea(options.area) + "/" + module + "/" + release
    assert os.path.isdir(prodPath), "Module %s doesn't exist in prod" % prodPath
    
    # Check the release isn't on the webserver
    webPath = "/dls_sw/cs-publish/downloads/%(area)s/%(module)s"%locals() 
    if os.path.isdir(webPath+"/"+release):
        msg = "%(module)s release %(release)s already exists on webserver" % locals()
        if options.force:
            print "Warning: "+msg+". Overwriting"
            shutil.rmtree("%(webPath)s/%(release)s"%locals())
        else:
            raise AssertionError, msg
    os.makedirs(webPath+"/"+release)    
    
    # Export to filesystem
    export = path+"/"+module+"-"+release    
    print 'Exporting to '+export+'...'
    if os.path.exists(export):
        shutil.rmtree("%(export)s"%locals())
    svn.export(source+"/"+release, export)

    # Remove the etc dir
    if os.path.isdir("%(export)s/etc"%locals()):
        shutil.rmtree("%(export)s/etc" % locals())
    
    # replace documentation with built version
    for docdir in docdirs:
        if os.path.exists(export+"/"+docdir):
            shutil.rmtree("%(export)s/%(docdir)s"%locals())
            shutil.copytree("%(prodPath)s/%(docdir)s"%locals(),"%(export)s/%(docdir)s"%locals())
            assert not os.system(r"find %(export)s/%(docdir)s -name '.svn' -prune -exec rm -rf {} \;"%locals()), \
                "Can't remove all .svn directories in documentation dir"
            if os.path.isdir("%(export)s/%(docdir)s/private"%locals()):                
                shutil.rmtree("%(export)s/%(docdir)s/private"%locals())
            assert not os.system("chmod -R ug+rwX,o+rX,o-w %(export)s"%locals()), \
                "Can't chmod the directory"    
            shutil.copytree("%(export)s/%(docdir)s"%locals(),"%(webPath)s/%(release)s/%(docdir)s"%locals())                    

    # add in iocs
    for ioc in os.listdir(prodPath + "/iocs"):
        if os.path.isdir(prodPath + "/iocs/" + ioc) and ioc not in os.listdir(export + "/iocs") and ioc != ".svn":
            shutil.copytree("%s/iocs/%s"%(prodPath,ioc),"%s/iocs/%s" % (export,ioc))
            assert not os.system(r"find %(export)s/iocs/%(ioc)s -name '.svn' -prune -exec rm -rf {} \;"%locals()), \
                "Can't remove all .svn directories in iocs dir"                    
            assert not os.system("make -C %(export)s/iocs/%(ioc)s clean uninstall > /dev/null" %locals()), \
                "Can't do a make clean uninstall on the ioc"

    # do any other steps
    if os.path.isfile("%(export)s/preparePublish.sh"%locals()):
        assert not os.system("cd %(export)s; ./preparePublish.sh" % locals()), \
            "Can't run the preparePublish.sh script in this module"
        os.remove("%(export)s/preparePublish.sh" % locals())
            
    # python files need the correct versioned setup.py
    if options.area == "python":
        shutil.copy("%(prodPath)s/setup.py"%locals(), "%(export)s/setup.py"%locals())
          
    # Zip up
    tgz = "%(path)s/%(module)s-%(release)s.tgz"%locals()
    print 'Zipping up...'
    assert not os.system("tar -czf %(tgz)s -C %(path)s %(module)s-%(release)s"%locals()), \
        "Can't zip the release"
    
    # put it on the webserver
    print 'Copying to '+webPath +'...'
    shutil.copy(tgz, "%(webPath)s/%(release)s"%locals())

    # regenerate the webpage
    print 'Generating releases page...'
    releases = e.sortReleases([x
        for x in os.listdir(webPath)
        if os.path.isdir(webPath+"/"+x) and x != ".svn"])
    releases.reverse()
    text = """<h2>Releases</h2>

<table id="releases" cellspacing="0" summary="releases">
  <tr>
    <th scope="col">Version</th>
    <th scope="col"><img src="../../img/archive.png" alt="icon"/>Source Code</th>
    <th scope="col"><img src="../../img/html.png" alt="icon"/>Documentation</th>
  </tr>
"""%locals()
    cls = ""
    for release in releases:
        text += '  <tr>\n'
        text += '    <td%(cls)s><strong>%(release)s</strong></td>\n'%locals()
        filename = "%(module)s-%(release)s.tgz"%locals()
        text += '    <td%(cls)s><a href="%(release)s/%(filename)s"><img src="../../img/archive.png" alt="icon"/>%(filename)s</a></td>\n'%locals()  
        text += '    <td%(cls)s>'%locals()
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
                text += '<a href="%(release)s/%(docpath)s/%(html)s.html"><img src="../../img/html.png" alt="icon"/>%(html)s</a>'%locals() 
                if len(htmls)>1:
                    text += '<br/>'
        elif pdfs:
            for pdf in pdfs:
                text += '<a href="%(release)s/%(docpath)s/%(pdf)s"><img src="../../img/pdficon_small.gif" alt="icon"/>%(pdf)s</a>'%locals()             
                if len(pdfs)>1:
                    text += '<br/>'
                
        else:
            text += "None"
        text += '</td>\n'            
        text += '  </tr>\n'
        if cls:
            cls = ""
        else:
            cls = ' class="alt"'
        
    text += "</table>\n"
    open(webPath+"/releases.html","w").write(text)   

    # generate an index page if one doesn't exist
    if not os.path.exists(webPath+"/index.php"):
        open(webPath+"/index.php", "w").write("""<?php 
$top = "../../..";
$module = "%(module)s";
include("../header.html");
?> 

<h1>%(module)s</h1>
<p>DESCRIPTION GOES HERE
</p>

<h2>Contact</h2>
<img src="../../names/Firstname.Lastname.png" alt="contact"/>

<?php include("releases.html"); ?> 

<h2>Release Notes</h2>

<h3>Release %(release)s</h3>
<ul>
<li>Initial release</li>
</ul>

<?php include($top . "/footer.html"); ?>""" % locals())
        indexwritten = True
    else:
        indexwritten = False        
    # clean up
    print "Cleaning up..."
    os.remove(tgz)
    shutil.rmtree("%(path)s/%(module)s-%(release)s"%locals())
    if indexwritten:
        print "Now edit %(webPath)s/index.php to describe your module, " \
            "and add it to the navigation bar in %(webPath)s/../header.html" % locals()
        print "You can create an email image by running:"
        print "  /dls_sw/work/common/scripts/email_obfusticate.sh firstname.lastname"     
    print "Please check http://controls.diamond.ac.uk then"
    print "  svn add %s"  % webPath   
    print "  svn commit %s/.." % webPath
    print "with a suitable comment when you are happy"
    
if __name__ == "__main__":
    sys.exit(cs_publish())
