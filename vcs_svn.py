import abc
from vcs import BaseVCS
from dls_environment.svn import svnClient

class vcs_svn(BaseVCS):

    def __init__(self):
        self.client = svnClient()


    def check_epics_version(self, src_dir, build_epics, epics_version):
        ''' Compare epics version on machine and requested, confirm choice '''
        print src_dir, build_epics, epics_version

        conf_release = self.client.cat(src_dir + "/configure/RELEASE")
        module_epics = re.findall(r"/dls_sw/epics/(R\d(?:\.\d+)+)/base",
                                  conf_release)
        if module_epics:
            module_epics = module_epics[0]
        if not epics_version and module_epics != build_epics:
            sure = raw_input(
                "You are trying to release a %s module under %s without "
                "using the -e flag. Are you sure [y/n]?" %
                (module_epics, build_epics)).lower()
            if sure != "y":
                sys.exit()


    def next_release(self, module, area):
        ''' Work out the release number by checking source directory '''
        print module, area

        release_paths = []
        source = self.client.prodModule(module, area)

        if self.client.pathcheck(source):
            for node, _ in self.client.list(source, \
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


    def pathcheck(self, path):
        ''' search for path '''
        self.client.pathcheck(path)


    def create_release(self, module, area, options):
        ''' create release of module using mkdir and copy '''
        print "this should use both mkdir and copy methods"
        raise NotImplementedError

        if options.next_version:
            version = next_release(module, area)
        if options.branch:
            src_dir = os.path.join(
                self.client.branchModule(module, area), options.branch)
        else:
            src_dir = self.client.devModule(module, area)
        rel_dir = os.path.join(self.client.prodModule(module, area), version)
        assert self.pathcheck(src_dir), \
            src_dir + ' does not exist in the repository.'

        if src_dir != rel_dir and not options.test_only:
            self.mkdir(self.client.prodModule(module, area))
            self.copy(src_dir,rel_dir)
            src_dir = rel_dir
            print "Created release in svn directory: " + rel_dir

    def mkdir(self, module, area):
        ''' svn specific; create new directory (used for creating release) '''
        self.client.mkdir(self.client.prodModule(module, area))


    def copy(self, src_dir, rel_dir):
        ''' svn specific; copy dir contents (used for creating release) '''
        self.client.copy(src_dir,rel_dir)


    def setLogMessage(self, message):
        ''' callback function to return message string for log '''
        self.client.setLogMessage(message)


# sanity check: ensure class fully implements the interface (abc)
assert issubclass(vcs_svn,BaseVCS)
