#!/bin/env dls-python
# This script comes from the dls_scripts python module

usage = """%prog [<module> <filename1> [<filename2> ... ]]

For each <filenamex>, backup <filenamex> to <filenamex>~, prepend the license 
text in a '#' commented block to <filenamex>. <module> is the module name that 
will appear in the license text."""

import sys, os, time
from optparse import OptionParser

def include_license():
    """Parse args, then prepend license text to the filename arguments"""
    parser = OptionParser(usage)
    parser.add_option("-c", dest="c", action="store_true", \
        help="Write license in a /*...*/ commented block instead of a '#' block")
    parser.add_option("-d", dest="doxygen", action="store_true", \
        help="Write a doxygen formatted license section to <filename1> in a /*...*/ block")
    parser.add_option("-l", dest="license", action="store_true", \
        help="Also copy the LGPL and GPL licenses to .")
    (options,args) = parser.parse_args()
    filenames = args[1:]
    if options.license:
        root = os.path.abspath(os.path.dirname(__file__))
        os.system("cp %(root)s/COPYING COPYING"%locals())
        os.system("cp %(root)s/COPYING.LESSER COPYING.LESSER"%locals())            
        print "Wrote COPYING, COPYING.LESSER"
    for filename in filenames:
        module = args[0]    
        lines = open(filename,"r").readlines()
        year = time.strftime("%Y")
        open(filename + "~","w").writelines(lines)
        print "Created backup of",filename+"~"
        if options.doxygen:
            open(filename,"w").writelines(lines+[dltext%locals()])
            return     
        licensetext = ltext%locals()          
        if options.c:
            licensetext = "/*\n"+licensetext.replace("#"," *")+" */\n"        
        if lines[0].startswith("#!"):
            open(filename,"w").writelines(lines[:1]+[licensetext]+lines[1:])
        else:
            open(filename,"w").writelines([licensetext]+lines)
        print "Prepended license to",filename

ltext = """# Author: Diamond Light Source, Copyright %(year)s
#
# License: This file is part of '%(module)s'
# 
# '%(module)s' is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# '%(module)s' is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public License
# along with '%(module)s'.  If not, see <http://www.gnu.org/licenses/>.
"""

dltext = """
\section License
    '%(module)s' is free software: you can redistribute it and/or modify
    it under the terms of the GNU Lesser General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    '%(module)s' is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public License
    along with '%(module)s'.  If not, see http://www.gnu.org/licenses/.
**/
"""
if __name__=="__main__":
    sys.exit(include_license())
