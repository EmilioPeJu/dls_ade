import os
from vcs import BaseVCS
from dls_environment.svn import svnClient


class Svn(BaseVCS):
    
    def __init__(self,module,options): #, client=svnClient()):
        '''
        'module' is string with module name to release/test.
        'options' is parse object containing options.
        Raises 'AssertionError' is svnClient.pathcheck fails to find repo path.
        '''
        self.client = svnClient()
        
        if options.branch:
            repo = os.path.join(
                self.client.branchModule(module, options.area),
                options.branch)
        else:
            repo = self.client.devModule(module,options.area)
        
        assert self.client.pathcheck(repo)


    # def cat(self, filename):
    #     ''' Fetch contents of file in remote repository '''
    #     return self.client.cat(filename)


    def list_releases(self, module, area):
        ''' Return list of releases of module '''
        release_paths = []
        source = self.client.prodModule(module, area)
        if self.client.pathcheck(source):
            for node, _ in self.client.list(
                    source,
                    depth=self.client.depth.immediates)[1:]:
                release_paths.append(os.path.basename(node.path))
        return release_paths


    # def path_check(self, path):
    #     ''' search for path '''
    #     return self.client.pathcheck(path)


    # def checkout_module(self, module, area, src_dir, rel_dir):
    #     ''' create release of module using mkdir and copy '''
    #     self.client.mkdir(self.client.prodModule(module,area))
    #     self.client.copy(src_dir,rel_dir)


    # def set_log_message(self, message):
    #     ''' callback function to return message string for log '''
    #     self.client.setLogMessage(message)


    # def get_src_dir(self, module, options):
    #     '''
    #     Find/create the source directory from which to release the module.
    #     '''
    #     if options.branch:
    #         return os.path.join(
    #             self.client.branchModule(module, options.area),
    #             options.branch)
    #     else:
    #         return self.client.devModule(module, options.area)


    # def get_rel_dir(self, module, options, version):
    #     '''
    #     Create the release directory the module will be released into.
    #     '''
    #     return os.path.join(
    #         self.client.prodModule(module, options.area),
    #         version)


# sanity check: ensure class fully implements the interface (abc)
assert issubclass(Svn, BaseVCS), "Svn is not a sub-class of BaseVCS"
