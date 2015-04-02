import os
from vcs import BaseVCS
from dls_environment.svn import svnClient


class Svn(BaseVCS):


    def __init__(self, module, options):
        '''
        'module' is string with module name to release/test.
        'options' is parse object containing options.
        '''
        self._module = module
        self.area = options.area
        self.client = svnClient()
        self.set_repository_url()
        self._version = None


    @property
    def vcs_type(self):
        return 'svn'


    @property
    def module(self):
        return self._module


    @property
    def source_repo(self):
        return self._repo_url.replace('svn+ssh://','http://').replace('/home/subversion','')


    @property
    def version(self):
        if not self._version:
            raise Exception('version not set')
        return self._version


    def set_repository_url(self):
        '''
        Raises 'AssertionError' if svnClient.pathcheck fails to find repo path.
        '''
        self._repo_url = self.client.devModule(self._module, self.area)
        assert self.client.pathcheck(self._repo_url), \
            "%s does not exist" % self._repo_url


    def cat(self, filename):
        '''Fetch contents of file in remote repository.'''
        return self.client.cat(os.path.join(self._repo_url, filename))


    def list_releases(self):
        '''Return list of releases of module.'''
        releases = []
        source = self.client.prodModule(self._module, self.area)
        if self.client.pathcheck(source):
            for node, _ in self.client.list(
                    source,
                    depth=self.client.depth.immediates)[1:]:
                releases.append(os.path.basename(node.path))
        return releases


    def set_log_message(self, message):
        '''callback function to return message string for log.'''
        self.client.setLogMessage(message)


    def check_version_exists(self, version):
        return version in self.list_releases()


    def set_branch(self, branch):
        '''
        Raises 'AssertionError' if branch url not found, else sets repo url.
        '''
        self._repo_url = os.path.join(
            self.client.branchModule(self._module, self.area), branch)
        assert self.client.pathcheck(self._repo_url), \
            'branch %s does not exist' % branch


    def set_version(self, version):
        '''
        Store version number to release under in vcs object.
        If version exists, set repository url to that release vrsion.
        '''
        self._version = version
        if self.check_version_exists(version):
            self._repo_url = os.path.join(
                self.client.prodModule(self._module, self.area), version)


    def release_version(self, version):
        '''Create release with version number in svn repository.'''
        release_url = os.path.join(
            self.client.prodModule(self._module, self.area),
            version)
        self.client.mkdir(release_url)
        self.client.copy(self._repo_url, release_url)
        self.set_version(version) # changes repo url to release version


# sanity check: ensure class fully implements the interface (abc)
assert issubclass(Svn, BaseVCS), "Svn is not a sub-class of BaseVCS"
