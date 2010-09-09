#!/bin/env dls-python
# This script comes from the dls_scripts python module

usage = """usage: %prog [options] <cfg_file> <pages_file>

Parse <cfg_file> and <pages_file>, add autogen stuff, and output to
<cfg_file>.replace('.src','.cfg') and <pages_file>.replace('.src',''). Finally, 
run doxygen on the generated config.src to generate files"""

import os, sys, glob, re
from pkg_resources import require

def make_config_dict(root = "../.."):
    """Make the Doxygen config dict from information on the current module.
    Assumes that $(pwd)/<root> is the module root"""
    root = os.path.abspath(root)    
    d = {}
    d["EXCLUDE"]    = " ".join(glob.glob(root+'/*App/src/*Main.cpp'))
    d["INPUT"]               = ". "
    for dname in ["src","Db","protocol","pmc"]:
        # parse *App/<dname>/* for doxygen comments
        d["INPUT"]          += " "+ (" ".join(glob.glob(root+"/*App/"+dname+"/")))    
    for dname in ["src"]:
        # parse <dname>/* for doxygen comments    
        d["INPUT"]          += " "+ (" ".join(glob.glob(root+"/"+dname+"/"))) 
    # setup the environment
    from dls_environment import environment        
    e = environment()
    module_name, module_version = e.classifyPath(root)
    # if the tree is invalid, check to see if what kind of module it is:
    version = ""
    if module_version == "invalid":
        for area in module_e.areas:
            if e.prodArea(area) in root:
                split = root.replace(e.prodArea(area),"").split("/")
                name = split[-2]
                version = split[-1]
            else:
                name = root.split("/")[-1]
    else:
        name = module_name
        if module_version not in ["work","local","invalid"]:
            version = module_version
    d["PROJECT_NAME"]        = name
    d["PROJECT_NUMBER"]      = version
    return d

def main():
    """Commandline doxygen config generator for dls builds"""
    # create and option parser
    from optparse import OptionParser
    parser = OptionParser(usage)
    parser.add_option("-o", dest="out", default=".", \
        help="Output directory, default is '.'")
    # parse arguments
    (options, args) = parser.parse_args()
    if len(args) < 2:
        parser.error("Incorrect number of arguments")
    config = args[0]
    manual = args[1]
    out = options.out
    print "Configuring Doxygen..."
    # make the config dict
    f = open(out+"/"+config.replace(".src",".cfg"),"w")
    # include diamond defaults
    import dls_scripts.input_filter        
    f.write("@INCLUDE_PATH = %s\n"%os.path.dirname(dls_scripts.input_filter.__file__))
    f.write("@INCLUDE = def_config.cfg\n")
    # make a filter from input_filter.py
    filtname = "doxygen_filter.sh"
    filt = open(out+"/"+filtname,"w")
    print >> filt, "#!/bin/env sh"
    print >> filt, 'PYTHONPATH=%s %s %s $1'%(require("iocbuilder")[0].location, sys.executable, dls_scripts.input_filter.__file__)
    filt.close()
    # tell doxygen to use the filter
    f.write("FILTER_PATTERNS = %s\n"%(" ".join("*.%s=./%s"%(e,filtname) for e in ["vdb","proto","protocol","template","db", "pmc"])))
    # if there's an image directory, include it
    imagepath = os.path.abspath(os.path.dirname(os.path.abspath(config))+"/images")
    if os.path.isdir(imagepath):
        f.write("IMAGE_PATH=%s\n"%imagepath)
    for k, v in make_config_dict().items():
        f.write("%-25s = %s\n"%(k,v))
    if out == ".":
        # hack for the old build system
        f.write(open("../"+config,"r").read())        
    else:        
        f.write(open(config,"r").read())
    f.close()
    # make the manual from manual.src and the auto generated build instructions
    f = open(out+"/"+manual.replace(".src",""),"w")
    # if we have any build instructions, then add them here
    if len(args) > 2:
         make_build_instructions(f,args[2])
    if out == ".":
        # hack for the old build system
        f.write(open("../"+manual,"r").read())        
    else:
        f.write(open(manual,"r").read())
    f.close()
    # Make the filter executable
    os.system("chmod +x "+out+"/"+filtname)    
    print "Running Doxygen..."
    os.system("cd %s; %s/doxygen config.cfg"%(out, os.path.dirname(sys.executable)))
    print "Done"

if __name__=="__main__":
    sys.exit(main())
