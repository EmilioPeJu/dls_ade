#!/bin/env python2.4
usage = """%prog [options] <template>

Print a template builder class from this db template file.
"""
import os, sys, re, glob
from optparse import OptionParser
from common import doc

all_protos = set()

sys.path.append("/dls_sw/tools/python2.4/lib/python2.4/site-packages/iocbuilder-2.2-py2.4.egg")
from iocbuilder.autosubst import populate_class

class cls:
    WarnMacros=False

@doc(usage)
def make_builder():
    parser = OptionParser(usage)
    parser.add_option("-o", "--out", action="store", type="string", dest="out", 
        help="Write to this output file instead of printing")    
    (options, args) = parser.parse_args()
    if len(args) != 1:
        parser.error("Incorrect number of arguments.")    
    text, imports, extext = make_builder_f(args[0])
    text = "%s\n\n%s" % ("\n".join(imports), text)
    if options.out:
        open(options.out, "w").write(text)
    else:
        print text
               
def make_builder_f(filename):        
    # get the template text
    text = open(filename).read()
    basename = os.path.basename(filename)
    clsname = basename.split(".")[0]
    modname = os.path.basename(os.path.abspath("."))
    populate_class(cls, filename)
    
    # find all protocol files
    protos = set(re.findall(r"@(.*\.proto[^ ]*)",text))
    global all_protos
    all_protos.update(protos)
    
    imports = ["from iocbuilder import AutoSubstitution"]
    if protos:
        deps = "AutoSubstitution, AutoProtocol"
        imports.append("from iocbuilder.modules.streamDevice import AutoProtocol")
    else:
        deps = "AutoSubstitution"
    text = ""
    text += "class %s(%s):\n" % (clsname, deps)
    text += "    # Substitution attributes\n"
    text += "    TemplateFile = '%s'\n"%basename  
    text += "\n"    
    if protos:
        text += "    # AutoProtocol attributes\n"
        text += "    ProtocolFiles = %s\n" % (list(protos).__repr__())
        text += "\n"    
    text += "\n"    
    extext = ""     
    if protos:
        p = list(protos)[0].split(".")[0]
        extext += '\t<pyDrv.serial_sim_instance module="%s_sim" name="%sSim" pyCls="%s"/>\n' % (p, clsname, p)
        extext += '\t<asyn.AsynIP name="%sAsyn" port="172.23.111.180:7001" simulation="%sSim"/>\n' %(clsname, p)        
    extext += "\t<%s.%s" % (modname, clsname)
    for macro in cls.ArgInfo.required_names:
        if macro.lower() == "port" and protos:
            extext += ' %s="%sAsyn"' % (macro, p)        
        else:
            extext += ' %s="%s"' % (macro, macro)
    extext +=  "/>\n"
    return text, imports, extext
    
if __name__ == "__main__":
    make_builder()    
