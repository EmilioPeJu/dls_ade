#!/bin/env dls-python2.6

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import os, sys, re, signal, time
from subprocess import Popen, PIPE
from optparse import OptionParser
from dls_environment import environment

usage = """%prog [ioc_filter_re]

This program interrogates configure-ioc for all IOCs that match ioc_filter_re,
then shows a gui with options to redirect iocs to different versions
"""

class MainWindow(QDialog):
    def __init__(self, r, show_sim, *args, **kwargs):
        QDialog.__init__(self, *args, **kwargs)
        self.r = re.compile(r)
        self.show_sim = show_sim
        self.e = environment()
        layout = QGridLayout()
        self.setLayout(layout)
        self.iocs, self.names, self.versions, self.exts, self.logs, self.logfs = [], [], [], [], [], []
        i = 0
        for i, (ioc, name, version, root, ext) in enumerate(self.getIocData()):
            self.iocs.append(QLabel(ioc + ":", self))
            layout.addWidget(self.iocs[-1], i, 0)
            self.names.append(QLabel(name, self))
            self.names[-1].setToolTip(self.iocData[i][3] + ext)
            layout.addWidget(self.names[-1], i, 1)             
            self.versions.append(QComboBox(self))
            versions = self.getVersions(i)
            self.versions[-1].addItems(versions)
            self.versions[-1].setCurrentIndex(versions.index(version))
            layout.addWidget(self.versions[-1], i, 2)             
            self.exts.append(QLineEdit(ext, self))
            layout.addWidget(self.exts[-1], i, 3)
            self.exts[-1].setMinimumWidth(QFontMetrics(QApplication.font()).width(ext)+10)
            self.logs.append(QPushButton("View Log", self))
            layout.addWidget(self.logs[-1], i, 4)
            def f(checked=False, i=i):
                self.svnLog(i)
            self.logfs.append(f)
            self.logs[-1].clicked.connect(self.logfs[-1])
        
    def getIocData(self):
        output = Popen(["configure-ioc", "l"], stdout=PIPE).communicate()[0]
        self.iocData = []
        self.paths = []
        for line in output.splitlines():
            ioc, path = line.split(" ",1)
            if self.r.match(ioc):
                if not self.show_sim and "-SIM" in ioc:
                    continue
                index = None
                for s in ["/bin/", "/data/"]:
                    if s in path:
                        index = path.find(s)
                        break
                if index:
                    ext = path[index:]
                    root = path[:index]
                    name, version = self.e.classifyPath(root)
                    matches = self.e.epics_ver_re.search(root)
                    if matches:
                        epicsVer = matches.group()
                    else:
                        epicsVer = self.e.epicsVer()
                    self.iocData.append((ioc, name, version, epicsVer, ext))
                    self.paths.append(path)
        return self.iocData

    def getVersions(self, i):
        e = self.e.copy()        
        e.setEpics(self.iocData[i][3])
        area = e.prodArea("ioc")
        releaseDir = os.path.join(e.prodArea("ioc"), self.iocData[i][1])
        versions = []        
        if os.path.isdir(releaseDir):
            versions = e.sortReleases(os.listdir(releaseDir))
            versions.reverse()
        if "work" not in versions:
            versions.append("work")
        if self.iocData[i][2] not in versions:
            versions.append(self.iocData[i][2])
        return versions
        
    def getChanges(self):
        for i in range(len(self.iocData)):
            e = self.e.copy()        
            e.setEpics(self.iocData[i][3])       
            ext = str(self.exts[i].text())
            version = str(self.versions[i].currentText())
            if version == "work":
                newPath = os.path.join(e.devArea("ioc"), self.iocData[i][1]) + ext
            elif version in ("local", "invalid"):
                newPath = self.paths[i]
            else:
                newPath = os.path.join(e.prodArea("ioc"), self.iocData[i][1], version) + ext
            if newPath != self.paths[i]:
                yield (self.iocData[i][0], self.paths[i], newPath)

    def writeChanges(self):
        text = ""
        for ioc, old, new in self.getChanges():
            text += "%s %s\n" %(ioc, new)
        if text:
            p = Popen(["configure-ioc", "b"], stdout = PIPE, stderr = PIPE, stdin = PIPE)
            (stdout, stderr) = p.communicate(text)
            text = stdout.strip()
        else:
            text = "No Changes"
        x = formLog(text,self)
        x.setWindowTitle("Result")
        x.show()         
    
    def showChanges(self):
        text = ""
        for ioc, old, new in self.getChanges():
            text += "%s: Change from \n    %s\nto\n    %s\n" %(ioc, old, new)
            if not os.path.isfile(new):
                text += "*** Warning: invalid path %s\n" % new
        if not text:
            text = "No Changes"
        x = formLog(text,self)
        x.setWindowTitle("Changes")
        x.show() 
        
    def svnLog(self, i):
        oldver = self.iocData[i][2]
        newver = str(self.versions[i].currentText())
        args = ["dls-logs-since-release.py","-i","-r",self.iocData[i][1]]
        if oldver != newver:
            if oldver not in ("local", "invalid", "work"):
                args.append(oldver)
                if newver not in ("local", "invalid", "work"):
                    args.append(newver)              
        p = Popen(args, stdout = PIPE, stderr = PIPE)
        (stdout, stderr) = p.communicate()
        text = stdout.strip()
        x = formLog(text,self)
        x.setWindowTitle("SVN Log: %s"%self.iocData[i][1])
        x.show() 

class formLog(QDialog):
    """SVN log form"""
    def __init__(self,text,*args):
        """text = text to display in a readonly QTextEdit"""
        QDialog.__init__(self,*args)
        formLayout = QGridLayout(self)#,1,1,11,6,"formLayout")
        self.scroll = QScrollArea(self)        
        self.lab = QTextEdit()
        self.lab.setFont(QFont('monospace', 10))
        self.lab.setText(text)
        self.lab.setReadOnly(True)
        self.scroll.setWidget(self.lab)
        self.scroll.setWidgetResizable(True)
        self.scroll.setMinimumWidth(800)        
        formLayout.addWidget(self.scroll,1,1)        
        self.btnClose = QPushButton("btnClose", self)
        formLayout.addWidget(self.btnClose,2,1)
        self.btnClose.clicked.connect(self.close)
        self.btnClose.setText("Close")



class Top(QDialog):
    def __init__(self, mw, *args, **kwargs):
        QDialog.__init__(self, *args, **kwargs)
        self.mw = mw
        sa = QScrollArea(self)
        sa.setWidgetResizable(True)
        sa.setWidget(self.mw)
        layout = QGridLayout(self)
        self.setLayout(layout)
        layout.addWidget(sa, 0, 0, 1, 3)        
        showChanges = QPushButton("Show Changes", self)
        layout.addWidget(showChanges, 1, 0)
        showChanges.clicked.connect(self.mw.showChanges)
        writeChanges = QPushButton("Write Changes", self)
        layout.addWidget(writeChanges, 1, 1)
        writeChanges.clicked.connect(self.mw.writeChanges)        
        close = QPushButton("Close", self)
        layout.addWidget(close, 1, 2)
        close.clicked.connect(self.close)        

if __name__ == "__main__":
    parser = OptionParser(usage)
    parser.add_option("-s", "--show-sim", action="store_true", dest="show_sim", help="Show Simulation IOCS")
    (options, args) = parser.parse_args()
    if len(args) not in range(2):
        parser.error("Invalid number of arguments")
    if args:
        r = args[0]
    else:
        r = "."
    app = QApplication([]) 
    window = MainWindow(r, options.show_sim)      
    top = Top(window)
    top.setWindowTitle("Configure IOCS: %s" % r)
    top.setMinimumWidth(1024) 
    top.show()
    # catch CTRL-C
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app.exec_()
