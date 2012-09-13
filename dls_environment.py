#!/usr/bin/env python2.4
# Author: Diamond Light Source, Copyright 2008
#
# License: This file is part of 'dls.environment'
#
# 'dls.environment' is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# 'dls.environment' is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with 'dls.environment'.  If not, see <http://www.gnu.org/licenses/>.

import os, shutil, re
from optparse import OptionParser
from subprocess import Popen, PIPE, STDOUT

class environment:
    """A class representing the epics environment of a site. epics=version of
    epics, e.g R3.14.8.2 If you modify this to suit your site environment, you
    will be able to use any of the dls modules without modification. This module
    has the idea of areas. An area is simply an argument that can be passed to
    devArea or prodArea. support and ioc must exist to use modules like the
    dependency checker, others may be added. For example the dls support devArea
    contains all support modules, and is located at
    /dls_sw/work/R3.14.8.2/support. This is the area for testing modules. There
    is a similar prodArea at /dls_sw/prod/R3.14.8.2/support for releases. These
    are then used to locate the root of a particular module.

    Variables
    epics: the version of epics
    epics_ver_re: a useful regex for matching the version of epics
    areas: the areas that can be passed to devArea() or prodArea()
    """

    def __init__(self,epics = None):
        self.epics = None
        self.epics_ver_re = re.compile(r"R\d(\.\d+)+")
        self.areas = ["support", "ioc", "matlab", "python","etc","build_scripts","epics"]
        if epics:
            self.setEpics(epics)

    def setEpicsFromEnv(self):
        """Try to get epics version from the environment, and set self.epics"""
        try:
            self.epics = os.environ['DLS_EPICS_RELEASE']
        except KeyError:
            try:
                self.epics = os.environ['EPICS_RELEASE']
            except KeyError:
                self.epics = 'R3.14.8.2'

    def copy(self):
        """Return a copy of self"""
        return environment(self.epicsVer())

    def setEpics(self,epics):
        """Force the version of epics in self"""
        self.epics = epics

    def epicsDir(self):
        """Return the root directory of the epics installation"""
        if self.epicsVer()<"R3.14":
            return os.path.join("/home","epics",self.epicsVerDir())
        else:
            return os.path.join("/dls_sw","epics",self.epicsVerDir())

    def epicsVer(self):
        """Return the version of epics from self. If it not set, try and get it
        from the environment. This may have a _64 suffix for 64 bit architectures"""
        if not self.epics:
            self.setEpicsFromEnv()
        return self.epics

    def epicsVerDir(self):
        """Return the directory version of epics from self. If it not set, try and get it
        from the environment. This will not have a _64 suffix for 64 bit architectures"""
        if not self.epics:
            self.setEpicsFromEnv()
        return self.epics.split("_")[0]

    def devArea(self,area = "support"):
        """Return the development directory for a particular area"""
        assert area in self.areas, "Only the following areas are supported: "+\
               ",".join(self.areas)
        if self.epicsVer()<"R3.14":
            if area in ["support","ioc"]:
                return os.path.join("/home","diamond",self.epicsVerDir(),"work",\
                                    area)
            elif area in ["epics","etc"]:
                return os.path.join("/home","work",area)
            else:
                return os.path.join("/home","diamond","common","work",area)
        else:
            if area in ["support","ioc"]:
                return os.path.join("/dls_sw","work",self.epicsVerDir(),area)
            elif area in ["epics", "etc"]:
                return os.path.join("/dls_sw","work",area)
            elif area in ["build_scripts"]:
                return os.path.join("/dls_sw","work","tools","RHEL5",area)
            else:
                return os.path.join("/dls_sw","work","common",area)

    def prodArea(self,area = "support"):
        """Return the production directory for a particular area"""
        if area in ["epics"]:
            return os.path.join("/dls_sw",area)
        else:
            return self.devArea(area).replace("work","prod")

    def sortReleases(self,releases):
        """Sort a list of release numbers or release paths or tuples of release
        paths with objects according to local rules, and return them in
        ascending order."""
        order = []
        # order = (1st,2nd,3rd,4th,5th,6th,suffix,path[,object])
        # e.g. ./4-5dls1-3-1 = (4,5,0,1,3,1,"release",./4-5dls1-3)
        for path in releases:
            try:
                if type(path) == tuple:
                    o = [0,0,0,0,0,0,"release",path[0],path[1]]
                    path = path[0]
                else:
                    o = [0,0,0,0,0,0,"release",path]
                version = os.path.basename(path.rstrip("/"))
                version = version.replace(".","-").replace("_","-")
                split = [x.split("-") for x in version.split("dls")]
                split0 = split[0]
                numre = re.compile("\d*")
                if len(split)>1:
                    split1 = split[1]
                    lastarray = split1
                else:
                    split1 = []
                    lastarray = split0
                lastnum = str(numre.findall(lastarray[-1])[0])
                if lastnum != lastarray[-1]:
                    # we have a bit of text on the end
                    o[6]=lastarray[-1].replace(lastnum,"")
                lastarray[-1]=lastnum
                for i,x in enumerate(split0):
                    try:
                        o[i]=int(x)
                    except ValueError:
                        pass
                for i,x in enumerate(split1):
                    try:
                        o[i+3]=int(x)
                    except ValueError:
                        pass
                order.append(tuple(o))
            except:
                order.append(tuple(o))
        order.sort()
        if len(order[0])>8:
            return [(x[7],x[8]) for x in order]
        else:
            return [x[7] for x in order]

    def svnName(self, path):
        """Find the name that the module is under in svn. Very dls specific"""
        output = Popen(["svn", "info", path], stdout=PIPE, stderr=STDOUT).communicate()[0]
        for line in output.splitlines():
            if line.startswith("URL:"):
                split = line.split("/")
                if "/branches/" in line:   
                    if len(split) > 1:                 
                        return split[-2].strip()
                else:
                    return split[-1].strip()    

    def classifyPath(self, path):
        """Classify the name and version of the path of the root of a module"""
        sections = path.rstrip("/").split("/")
        if self.prodArea("support") in path:
            if len(sections) - len(self.prodArea("support").split("/")) == 2: 
                name = sections[-2]
                version = sections[-1]
            else:
                name = sections[-1]
                version = "invalid"
        elif self.prodArea("ioc") in path:
            if len(sections) - len(self.prodArea("ioc").split("/")) == 3:         
                name = sections[-3]+"/"+sections[-2]
                version = sections[-1]
            else:
                name = sections[-2]+"/"+sections[-1]
                version = "invalid"
        else:
            name = self.svnName(path)
            if not name:
                name = sections[-1]
            if self.devArea("support") in path:
                if len(sections) - len(self.devArea("support").split("/")) == 1:                    
                    version = "work"
                else:
                    version = "invalid"
            elif self.devArea("ioc") in path:
                name = sections[-2]+"/"+name            
                if len(sections) - len(self.devArea("ioc").split("/")) == 2:                    
                    version = "work"
                else:
                    version = "invalid"
            else:
                if "ioc" in path:
                    name = sections[-2]+"/"+name
                version = "local"
        return (name, version)

if __name__=="__main__":
    # test
    e = environment("R3.14.8.2")
    print "epics:",e.epicsVer()

    for area in e.areas:
        print "Production  directory for area %s is %s"%(area,e.prodArea(area))
        print "Development directory for area %s is %s"%(area,e.devArea(area))
        print
