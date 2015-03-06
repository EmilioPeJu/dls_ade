import os
from vcs import BaseVCS
from dls_environment.svn import svnClient


class Svn(BaseVCS):


    def __init__(self, module, options):
        '''
        'module' is string with module name to release/test.
        'options' is parse object containing options.
        '''
        self.vcs_type = 'svn'
        self.module = module
        self.area = options.area
        self.init_client(options.branch)


    def init_client(self, branch):
        '''
        Raises 'AssertionError' is svnClient.pathcheck fails to find repo path.
        '''
        self.client = svnClient()
        if branch:
            repo = os.path.join(
                self.client.branchModule(self.module, self.area),
                branch)
        else:
            repo = self.client.devModule(self.module, self.area)
        
        assert self.client.pathcheck(repo), "%s does not exist" % repo


    def cat(self, filename, _):
        ''' Fetch contents of file in remote repository '''
        return self.client.cat(filename)


    def list_releases(self):
        ''' Return list of releases of module '''
        if not hasattr(self, 'releases'):
            self.releases = []
            source = self.client.prodModule(self.module, self.area)
            if self.client.pathcheck(source):
                for node, _ in self.client.list(
                        source,
                        depth=self.client.depth.immediates)[1:]:
                    self.releases.append(os.path.basename(node.path))
        return self.releases


    def set_log_message(self, message):
        ''' callback function to return message string for log '''
        self.client.setLogMessage(message)


    def check_version_exists(self, version):
        return version in self.list_releases()


# sanity check: ensure class fully implements the interface (abc)
assert issubclass(Svn, BaseVCS), "Svn is not a sub-class of BaseVCS"
