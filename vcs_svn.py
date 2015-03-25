import os
from vcs import BaseVCS
from dls_environment.svn import svnClient


class Svn(BaseVCS):


    def __init__(self, module, options):
        '''
        'module' is string with module name to release/test.
        'options' is parse object containing options.
        '''
        self.module = module
        self.area = options.area
        self.init_client(options.branch)

    @property
    def vcs_type(self):
        return 'svn'

    def init_client(self, branch):
        '''
        Raises 'AssertionError' is svnClient.pathcheck fails to find repo path.
        '''
        self.client = svnClient()
        if branch:
            self.repo_url = os.path.join(
                self.client.branchModule(self.module, self.area),
                branch)
        else:
            self.repo_url = self.client.devModule(self.module, self.area)

        assert self.client.pathcheck(self.repo_url), \
            "%s does not exist" % self.repo_url


    def cat(self, filename, _):
        ''' Fetch contents of file in remote repository '''
        return self.client.cat(os.path.join(self.repo_url, filename))


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


    def source_repo(self):
        return self.repo_url.replace('svn+ssh://','http://')


# sanity check: ensure class fully implements the interface (abc)
assert issubclass(Svn, BaseVCS), "Svn is not a sub-class of BaseVCS"
