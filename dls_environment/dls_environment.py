#!/usr/bin/env dls-python
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
        self.areas = ["support", "ioc", "matlab", "python","etc","tools","epics"]
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
            elif area in ["epics","etc", "tools"]:
                return os.path.join("/home","work",area)
            else:
                return os.path.join("/home","diamond","common","work",area)
        else:
            if area in ["support","ioc"]:
                return os.path.join("/dls_sw","work",self.epicsVerDir(),area)
            elif area in ["epics", "etc", "tools"]:
                return os.path.join("/dls_sw","work",area)
            else:
                return os.path.join("/dls_sw","work","common",area)

    def prodArea(self,area = "support"):
        """Return the production directory for a particular area"""
        if area in ["epics"]:
            return os.path.join("/dls_sw",area)
        else:
            return self.devArea(area).replace("work","prod")

    def normaliseRelease(self, release):
        """This function takes a release number, and returns a list of
        component parts that are then sortable by python's inbuild sort function
        E.g. 4-5beta2dls1-3 => [4,'z',5,'beta2z',0,'',1,'z',3,'z',0,'']
        The z allows us to sort alpha, beta and release candidates before
        release numbers without a text suffix"""
        components = []
        # first split by dls
        for part in release.split("dls", 1):
            # rejig separators
            part = part.replace(".","-").replace("_","-")
            # allow up to 3 -'s
            for subpart in part.split("-", 3):
                match = re.match("\d+", subpart)
                if match:
                    # turn the digit to an int so it sorts properly
                    components.append(int(match.group()))
                    components.append(subpart[match.start()+1:] + "z")
                else:
                    # just add the string part
                    components.append(0)
                    components.append(subpart)
            # pad to 6 elements
            components += [0, '']*(6-len(components))
        # pad to 12 elements
        components += [0, '']*(12-len(components))
        return components
            
    def sortReleases(self, paths):
        """Sort a list of paths by their release numbers. Assume that the
        paths end in a release number"""
        releases = []
        istuple = paths and type(paths[0]) == tuple
        for path in paths:
            if type(path) == tuple:
                release = os.path.split(os.path.normpath(path[0]))[1]
            else:
                release = os.path.split(os.path.normpath(path))[1]
            releases.append((self.normaliseRelease(release), path))
        return [x[1] for x in sorted(releases)]
        
    def svnName(self, path):
        """Find the name that the module is under in svn. Very dls specific"""
        output = Popen(["svn", "info", path], stdout=PIPE, stderr=STDOUT).communicate()[0]
        for line in output.splitlines():
            if line.startswith("URL:"):
                split = line.split("/")
                if "/branches/" in line or "/release/" in line:   
                    if "/ioc/" in line and len(split) > 2:
                        return "/".join((split[-3].strip(), split[-2].strip()))
                    elif len(split) > 1:                 
                        return split[-2].strip()
                else:
                    if "/ioc/" in line and len(split) > 1:
                        return "/".join((split[-2].strip(), split[-1].strip()))                
                    else:
                        return split[-1].strip()    

    def classifyArea(self, path):
        """Classify the area of a path, returning
        (area, work/prod/invalid, epicsVer)"""
        for a in self.areas:
            if path.startswith(self.devArea(a)):
                return (a, "work", self.epicsVer())
            elif path.startswith(self.prodArea(a)):
                return (a, "prod", self.epicsVer())
            elif a in path:
                area = a
        # not found, so strip epicsVer out and try again
        match = self.epics_ver_re.search(path)
        if match and match.group() != self.epicsVer():
            return self.__class__(match.group()).classifyArea(path)
        else:
            return ("invalid", "invalid", self.epicsVer())

    def classifyPath(self, path):
        """Return a (module, version) tuple for the path, where 
        version is "invalid", "work", or a version number"""
        # classify the area
        (area, domain, epicsVer) = self.classifyArea(path)
        e = self
        if epicsVer != self.epicsVer:
            e = self.__class__(epicsVer)
        # try and find the name in svn
        module = self.svnName(path)
        # deal with valid domains
        if domain == "work":
            root = e.devArea(area)
        elif domain == "prod":
            root = e.prodArea(area)
        else:
            root = ""
        assert path.startswith(root), "'%s' should start with '%s'" %(path,root)           
        sections = os.path.normpath(path[len(root):]).strip(os.sep).split(os.sep)
        # check they are the right length
        if domain == "work":        
            if len(sections) == 1 or area in [ "ioc", "tools", "python" ] and len(sections) == 2:
                version = "work"
            else:
                version = "invalid"
        elif domain == "prod":
            if len(sections) == 2 or area in [ "ioc", "tools", "python" ] and len(sections) == 3:                
                version = sections[-1]
                module = os.sep.join(sections[:-1])
                if area in [ "tools", "python"]:
                    module = sections[-2]
                else:
                    module = os.sep.join(sections[:-1])
            else:
                version = "invalid"
                sections = sections[:-1]
        else:
            version = "invalid"
        if module is None:
            if area == "ioc":
                module = os.sep.join(sections[-2:])
            elif len(sections) > 1:
                module = sections[-1]
        return (module, version)


if __name__=="__main__":
    # test
    e = environment("R3.14.11")
    print "epics:",e.epicsVer()

    for area in e.areas:
        print "Production  directory for area %s is %s"%(area,e.prodArea(area))
        print "Development directory for area %s is %s"%(area,e.devArea(area))
        print
        
    print e.classifyPath("/dls_sw/prod/R3.14.12.3/support/asyn/4-21")
    print e.classifyArea("/dls_sw/prod/tools/RHEL6-x86_64/boost/1-48-0")
    print e.classifyPath("/dls_sw/prod/tools/RHEL6-x86_64/boost/1-48-0")
    print e.classifyPath("/dls_sw/prod/common/python/RHEL6-x86_64/boost/1-48-0")
    print e.classifyPath("/dls_sw/work/tools/RHEL6-x86_64/boost")
    print e.classifyPath("/dls_sw/prod/common/python/RHEL6-x86_64/dls_environment/4-6")

