import os
import platform
import time
import getpass
import subprocess
import ldap
import tempfile
import stat
import shutil

from dls_environment import environment

build_scripts = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), "dlsbuild_scripts")


# Root directory to perform build operations.
# For testing/development, this can be changed to redirect build scripts away
# from the build server, e.g. a user's home directory. Just be sure that it
# contains the expected directories (e.g. work/etc/build/queue).
# Similarly defined for windows, as it replaces the root dir in the windows
# builder method.
root_dir = "/tmp"#"/dls_sw"
windows_root_dir = "W:/"

# A list of build servers and the EPICS releases they support
build_servers = {
    "Linux": {
        "redhat4-i686"   : ["R3.14.9"],
        "redhat5-i686"   : ["R3.14.8.2", "R3.14.11", "R3.14.10", "R3.14.12.1"],
        "redhat5-x86_64" : ["R3.14.11_64"],
        "redhat6-x86_64" : ["R3.14.12.3"]
    },
    "Windows": {
        "windows5-x86"   : ["R3.14.11", "R3.14.10", "R3.14.12.1"],
        "windows6-x86"   : ["R3.14.12.3"],
        "windows6-AMD64" : ["R3.14.12.3", "R3.14.12.1"]
    }
}


def epics_servers(os, epics):
    """Return list of servers that can build a version of epics"""
    servers = build_servers[os]
    servers = [s for s in servers if epics in servers[s]]
    return servers

server_shortcut = {
    "4": "redhat5-i686",
    "5": "redhat5-i686",
    "5_64": "redhat5-x86_64",
    "6": "redhat6-x86_64",
    "32": "windows6-x86",
    "64": "windows6-AMD64"}

os_list = set(os.listdir(build_scripts))
os_list -= set([".svn"])
svn_rw = os.environ["SVN_ROOT"]
svn_ro = "http://serv0002.cs.diamond.ac.uk/repos/controls"


def default_build(epics):
    """Return the default build object for this platform"""
    os = platform.system()
    if os == "Windows":
        return WindowsBuild(None, epics)
    else:
        return RedhatBuild(None, epics)


def default_server():
    """Return the default server for this machine"""
    os = platform.system()
    if os == "Windows":
        server = "windows%s-%s" % (
            platform.version().split(".")[0], platform.machine())
        return WindowsBuild(server, epics)
    else:
        server = "%s%s-%s" % (
            platform.dist()[0], platform.dist()[1].split(".")[0],
            platform.machine())
    return server


def get_email(user):
    """Get a users email address from Active directory using LDAP"""
    try:
        # Try and get email from Active DIrectory
        l = ldap.initialize('ldap://altfed.cclrc.ac.uk')
        result = l.search_s(
            "OU=DLS,DC=fed,DC=cclrc,DC=ac,DC=uk",
            ldap.SCOPE_SUBTREE, "(CN=%s)" % user, ['mail'])
        # Just return the first result from the result structure
        return result[0][1]["mail"][0]
    except:
        # Return default email address
        return "%s@rl.ac.uk" % user


class Builder:
    "Base class for Diamond build server submissions"

    def __init__(self, bld_os, server=None, epics=None):
        if server in server_shortcut.keys():
            server = server_shortcut[server]
        assert bld_os in os_list, "Build operating system not supported"

        self.os = bld_os
        self.force = False
        self.area = ""
        self.user = getpass.getuser()
        self.email = get_email(self.user)
        self.dls_env = environment()

        if epics is None:
            # if we have not specifier the epics version
            if server is None:
                # use the default server and epics from env
                self.server = default_server()
                # override to allow R3.14.11 to build on i686 by default
                if self.server == "redhat5-x86_64" and \
                        self.epics() in ["R3.14.11", "R3.14.12.1"] and \
                        os.environ["EPICS_HOST_ARCH"] == "linux-x86":
                    self.server = "redhat5-i686"
            else:
                # set specified server
                self.server = server
            # set epics from server
            if self.epics() not in build_servers[self.os][self.server]:
                self.set_epics(build_servers[self.os][self.server][0])
        else:
            # if we have specified epics version then set it
            self.set_epics(epics)
            if server is None:
                # set server from epics
                self.server = default_server()
                if self.epics() not in build_servers[self.os][self.server]:
                    servers = epics_servers(self.os, self.epics())
                    assert servers, \
                        "No %s build servers exist for epics version %s" % \
                        (self.os, self.epics())
                    self.server = servers[0]
            else:
                # set specified server
                self.server = server

        assert self.server in build_servers[self.os].keys(), \
            "No build server for this OS server: %s" % self.server
        assert self.epics() in build_servers[self.os][self.server], \
            "EPICS version %s not allowed for server %s" % (
                self.epics(),
                self.server)

    def set_area(self, area):
        """Sets the release area to use in the build"""
        file_list = os.listdir(os.path.join(build_scripts, self.os))
        script_list = [x for x in file_list if x.endswith(self.exten)]

        assert area + self.exten in script_list, \
            "Area %s is not supported for %s builds." % (area, self.os)

        self.area = area

    def set_epics(self, epics):
        """Sets the version of EPICS to use in the build"""
        self.dls_env.setEpics(epics)

    def set_force(self, force):
        self.force = force

    def build_servers(self):
        """Returns a list if the available build servers that can be used for
        the build"""
        return build_servers

    def get_server(self):
        """Returns the build server to use in the build"""
        return self.server

    def epics(self):
        """Returns the version of EPICS to use in the build"""
        return self.dls_env.epicsVer()

    def os_list(self):
        """Returns the list of operating systems supported"""
        return os_list

    def script_file(self):
        """Returns the files system path to the raw build script file"""
        return os.path.join(build_scripts, self.os, self.area+self.exten)

    def _script(self, params, header, format):
        """Returns the build script with headers and variables defined"""
        script = header+"\n\n"

        for name in params.keys():
            script += format % ("_" + name, params[name]+"\n")

        for line in file(self.script_file()):
            script += line

        return script

    def build_name(self, build, module, version):
        return "_".join([
            build, time.strftime("%Y%m%d-%H%M%S"),
            self.user, self.area, module.replace("/", "_"), version])

    def build_params(self, build_dir, vcs, version, build_name):
        return {
            "email"                 : self.email,
            "epics"                 : self.dls_env.epicsVer(),
            "build_dir"             : build_dir,
            "%s_dir"%vcs.vcs_type   : vcs.source_repo(),
            "module"                : vcs.module,
            "version"               : version,
            "area"                  : self.area,
            "force"                 : "true" if self.force else "false",
            "build_name"            : build_name}

    def local_test_possible(self):
        """Returns True if a local test build is possible"""
        local = default_server()
        remote = self.get_server()
        return local == remote or (
            local == "redhat5-x86_64" and remote == "redhat5-i686")

    def test(self, vcs, version):
        """Builds module version on the local system using the code in the
        src_dir directory of subversion."""

        build_name = self.build_name("local", vcs.module, version)
        build_dir = os.path.join(
            root_dir, "work", "etc", "build", "test", build_name)

        print "Test build of module in "+build_dir

        params = self.build_params(
            build_dir, vcs, version, build_name)

        dirname = tempfile.mkdtemp()
        filename = os.path.join(dirname, build_name+self.exten)
        print "Got build file "+filename+" to build module in "+build_dir
        f = open(filename, "w")
        f.write(self.build_script(params))
        f.close()
        os.chmod(filename, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)

        print "Created build file "+filename+" to build module in "+build_dir
        print "Performing local test build..."
        status = subprocess.call("/bin/env -i "+filename, shell=True)
        if status != 0:
            print "Local test build failed. Results are in "+build_dir
        else:
            print "Local test build succeeded"
            shutil.rmtree(build_dir)
        return status

    def submit(self, vcs, version, test=False):
        """Submit a job to the build queue to build module version using the
        code in the src_dir directory of subversion. If test="work" then the
        module is built in work, if it is anything else that evaluates to True
        it is built in the test directory. Otherwise it is a normal production
        build."""

        build_name = self.build_name("build", vcs.module, version)
        if test == "work":
            build_dir = self.dls_env.devArea(self.area)
        elif test:
            build_dir = os.path.join(
                root_dir, "work", "etc", "build", "test", build_name)
        else:
            build_dir = self.dls_env.prodArea(self.area)

        params = self.build_params(
            build_dir, vcs, version, build_name)

        # generate the filename
        pathname = os.path.join(root_dir, "work", "etc", "build", "queue")
        filename = "%s.%s" % (params["build_name"], self.server)
        print pathname, filename

        # Submit the build script
        f = open(os.path.join(pathname, filename), "w")
        f.write(self.build_script(params))
        f.close()

        # Create a log of the build
        f = file(
            os.path.expanduser(os.path.join("~", ".dls-release-log")),
            "a")
        f.write(" ".join([
            params["build_dir"], params["module"], params["version"],
            params["build_name"], self.server]) + "\n")
        f.close()

        print "Build request file: %s\nCreated in : %s" % (filename, pathname)


class WindowsBuild(Builder):
    """Implements the build class for Windows"""
    def __init__(self, server, epics):
        Builder.__init__(self, "Windows", server, epics)
        self.exten = ".bat"

    def build_script(self, params):
        for name in params.keys():
            if params[name][:1] == "/":
                params[name] = params[name].replace(root_dir, windows_root_dir)

        if self.server == "windows5-x86":
            params["make"] = "mingw32-make"
        else:
            params["make"] = "make"

        return Builder._script(self, params, "@echo on", "set %s=%s")


class RedhatBuild(Builder):
    """Implements the build class for Red Hat"""
    def __init__(self, server, epics):
        Builder.__init__(self, "Linux", server, epics)
        self.exten = ".sh"

    def build_script(self, params):
        return Builder._script(self, params, "#!/bin/bash", "%s=%s")


class ArchiveBuild(Builder):
    """Implements the build class for archiving or de-archiving modules. The
    constructor takes a single parameter which, if true, dearchives, otherwise
    the module will be archived."""
    def __init__(self, untar):
        Builder.__init__(self, "Linux", "redhat5-i686")
        self.exten = ".sh"
        self.action = "unarchive" if untar else "archive"

    def build_script(self, params):
        params["action"] = self.action
        return Builder._script(self, params, "#!/bin/bash", "%s=%s")

    def script_file(self):
        return os.path.join(build_scripts, self.os, "archive.sh")


if __name__ == "__main__":
    # test
    bld = WindowsBuild("64")
    bld.set_area("support")
    bld.set_epics("R3.14.12.1")
    print "build_script is:\n"+bld.build_script({"test" : root_dir+"/test"})

    bld = ArchiveBuild(True)
    bld.set_area("archive")
    bld.set_epics("R3.14.12.1")
    print "build_script is:\n"+bld.build_script({"test" : root_dir+"/test"})
