import os
from vcs import BaseVCS
from dls_environment.svn import svnClient


class Svn(BaseVCS):


    def __init__(self, module, options):
        '''
        'module' is string with module name to release/test.
        'options' is parse object containing options.
        Raises 'AssertionError' is svnClient.pathcheck fails to find repo path.
        '''
        self.vcs_type = 'svn'
        self.client = svnClient()
        if options.branch:
            repo = os.path.join(
                self.client.branchModule(module, options.area),
                options.branch)
        else:
            repo = self.client.devModule(module, options.area)
        assert self.client.pathcheck(repo), "%s does not exist" % repo


    def cat(self, filename, _):
        ''' Fetch contents of file in remote repository '''
        return self.client.cat(filename)


    def list_releases(self, module, area):
        ''' Return list of releases of module '''
        releases = []
        source = self.client.prodModule(module, area)
        if self.client.pathcheck(source):
            for node, _ in self.client.list(
                    source,
                    depth=self.client.depth.immediates)[1:]:
                releases.append(os.path.basename(node.path))
        return releases


    def set_log_message(self, message):
        ''' callback function to return message string for log '''
        self.client.setLogMessage(message)


    def check_version_exists(self, version):
        pass


# sanity check: ensure class fully implements the interface (abc)
assert issubclass(Svn, BaseVCS), "Svn is not a sub-class of BaseVCS"
