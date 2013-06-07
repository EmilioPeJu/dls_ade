#!/bin/env dls-python
# This script comes from the dls_scripts python module

usage = """%prog [options] <module_name> <branch_name>

Default <area> is 'support'.
Start a new feature branch, used to create a branch from the trunk.
The script copies the trunk of the current module into a new branch <branch_name>, reflecting the current changes."""

import os, sys, shutil

def start_feature_branch():
    from dls_environment.options import OptionParser
    parser = OptionParser(usage)
    (options, args) = parser.parse_args()
    if len(args)!=2:
        parser.error("Incorrect number of arguments.")

    # setup the environment
    module = args[0]
    branch_name = args[1]
    
    # import svn client
    from dls_environment.svn import svnClient    
    svn = svnClient()
    svn.setLogMessage(module + ": creating feature branch "+branch_name)
    if options.area == "ioc":
        assert len(module.split('/'))>1, 'Missing Technical Area under Beamline'
    source = svn.devModule(module,options.area)
    branch = os.path.join(svn.branchModule(module,options.area),branch_name)

    # Check for existence of release in svn, non-existence of branch in svn and current directory
    assert svn.pathcheck(source), 'Repository does not contain "'+source+'"'
    assert not svn.pathcheck(branch), 'Repository already contains "'+branch+'"'
    assert not os.path.isdir(branch.split("/")[-1]), branch.split("/")[-1]+" already exists in this directory. Please choose another name or move elsewhere."

    # make the branches directory
    svn.mkdir(svn.branchModule(module,options.area))
    svn.copy(source,branch)

    # checkout module
    tempdir = os.path.join('/tmp/svn',branch_name)
    if os.path.isdir(tempdir):
        shutil.rmtree(tempdir)
    svn.checkout(branch,tempdir)
    entry = svn.info(tempdir)

    # Find the revision number from "info" and set the property "dls:synced-from-trunk"
    # to this value. This property tells us how far up the trunk we have merged into
    # this branch.
    print 'Setting "dls:synced-from-trunk" property for this branch'
    svn.propset('dls:synced-from-trunk',str(entry.revision.number),tempdir,svn.Revision(svn.opt_revision_kind.working))
    mess = module+ '/' +branch_name+ ': Setting synced-from-trunk property'
    svn.checkin( tempdir, mess, True )
    shutil.rmtree(tempdir)
    print

    # Is the current directory a working SVN directory?
    isWC = svn.workingCopy()
    if isWC:
        if isWC.url == source:
        # if the directory is a WC of the source check for modified files
            status_list = svn.status( '.', True, True, True, True )
            for x in status_list:
                if str(x.repos_text_status) == 'modified':
                    print 'The file "' +x.path+ '" has been modified in the trunk,'
                    print 'therefore cannot switch this working SVN directory to the new branch'
                    print
                    print 'To create a working directory from the new branch'
                    print 'change directories and run:'
                    print 'svn checkout '+ branch
                    return
            # if no files have been modified ask to switch the directory to the branch
            print 'This is an SVN working directory for:'
            print '"' + source + '"'
            ans = raw_input('Do you want to switch this working directory onto the new branch? ')
            if ans.upper() in ["Y","YES"]:
                print 'Switching this working directory to the new branch ' + args[1]
                svn.switch( '.', branch)
            else:
                print 'NOT switching this working directory to the new branch'
                print
                print 'To create a working directory from this new branch,'
                print 'change directories and run:'
                print 'svn checkout '+ branch
        else:
        # if it is a WC of somewhere else then just leave it
            print 'This is an SVN working directory but not for:'
            print '"' + source + '"'
            print
            print 'To create a working directory from this new branch,'
            print 'change directories and run:'
            print 'svn checkout '+ branch
    else:
    # check out the branch to ./module/branch_name
        print 'Checking out:' 
        print branch + '...'
        svn.checkout(branch,branch.split("/")[-1])

if __name__ == "__main__":
    sys.exit(start_feature_branch())
