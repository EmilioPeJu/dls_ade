import abc
import os
import re
from vcs import BaseVCS
from dls_environment.svn import svnClient


class Svn(BaseVCS):

    def __init__(self):
        self.client = svnClient()


    def cat(self, filename):
        ''' Fetch contents of particular file in remote repository '''
        return self.client.cat(filename)


    def next_release(self, module, area):
        ''' Work out the release number by checking source directory '''
        print module, area

        release_paths = []
        source = self.client.prodModule(module, area)

        if self.client.pathcheck(source):
            for node, _ in self.client.list(
                    source,
                    depth=self.client.depth.immediates)[1:]:
                release_paths.append(os.path.basename(node.path))

        if len(release_paths) == 0:
                version = "0-1"
        else:
            from dls_environment import environment
            last_release = environment().sortReleases(release_paths)[-1]. \
                split("/")[-1]
            print "Last release for %s was %s" % (module, last_release)
            numre = re.compile("\d+|[^\d]+")
            tokens = numre.findall(last_release)
            for i in range(0, len(tokens), -1):
                if tokens[i].isdigit():
                    tokens[i] = str(int(tokens[i]) + 1)
                    break
            version = "".join(tokens)

        return version


    def path_check(self, path):
        ''' search for path '''
        return self.client.pathcheck(path)


    def checkout_module(self, module, area, src_dir, rel_dir):
        ''' create release of module using mkdir and copy '''
        self.mkdir(self.client.prodModule(module, area))
        self.copy(src_dir, rel_dir)


    def mkdir(self, module, area):
        ''' svn specific; create new directory (used for creating release) '''
        self.client.mkdir(self.client.prodModule(module, area))


    def copy(self, src_dir, rel_dir):
        ''' svn specific; copy dir contents (used for creating release) '''
        self.client.copy(src_dir, rel_dir)


    def set_log_message(self, message):
        ''' callback function to return message string for log '''
        self.client.setLogMessage(message)


    def get_src_dir(self, module, options):
        '''
        Find/create the source directory from which to release the module.
        '''
        if options.branch:
            return os.path.join(
                self.client.branchModule(module, options.area),
                options.branch)
        else:
            return self.client.devModule(module, options.area)


    def get_rel_dir(self, module, options, version):
        '''
        Create the release directory the module will be released into.
        '''
        return os.path.join(
            self.client.prodModule(module, options.area),
            version)


# sanity check: ensure class fully implements the interface (abc)
assert issubclass(Svn, BaseVCS)
