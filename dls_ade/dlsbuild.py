import os
import platform
import time
import getpass
import subprocess
import tempfile
import stat
import shutil
import ldap
import logging

from dls_ade.constants import BUILD_SERVERS, SERVER_SHORTCUT, DLSBUILD_ROOT_DIR, DLSBUILD_WIN_ROOT_DIR, LDAP_SERVER_URL, SYSLOG_SERVER, SYSLOG_SERVER_PORT
from dls_ade.dls_environment import environment

# Optional but useful in a library or non-main module:
logging.getLogger(__name__).addHandler(logging.NullHandler())
log = logging.getLogger(__name__)
usermsg = logging.getLogger("usermessages")

build_scripts = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), "dlsbuild_scripts")
os_list = set(os.listdir(build_scripts))
os_list -= set([".svn"])


def epics_servers(os, epics):
    """Return list of servers that can build a version of epics"""
    servers = BUILD_SERVERS[os]
    servers = [s for s in servers if epics in servers[s]]
    return servers


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
    else:
        server = "%s%s-%s" % (
            platform.dist()[0], platform.dist()[1].split(".")[0],
            platform.machine())
    return server


def get_email(user):
    """Get a users email address from Active directory using LDAP"""
    try:
        # Try and get email from Active DIrectory
        l = ldap.initialize(LDAP_SERVER_URL)
        result = l.search_s(
            "OU=DLS,DC=fed,DC=cclrc,DC=ac,DC=uk",
            ldap.SCOPE_SUBTREE, "(CN=%s)" % user, ['mail'])
        # Just return the first result from the result structure
        return result[0][1]["mail"][0].decode('ascii')
    except:
        # Return default email address
        return "%s@rl.ac.uk" % user


class Builder:
    "Base class for Diamond build server submissions"

    def __init__(self, bld_os, server=None, epics=None):

        assert bld_os in os_list, "Build operating system not supported"

        self.os = bld_os
        self.force = False
        self.area = ""
        self.user = getpass.getuser()
        self.email = get_email(self.user)
        self.dls_env = environment()

        if server:
            self.dls_env.check_rhel_version(server)

        if server in SERVER_SHORTCUT.keys():
            server = SERVER_SHORTCUT[server]

        if epics is None:
            # if we have not specifier the epics version
            if server is None:
                # use the default server and epics from env
                self.server = default_server()
            else:
                # set specified server
                self.server = server
            # set epics from server
            if self.epics() not in BUILD_SERVERS[self.os][self.server]:
                self.set_epics(BUILD_SERVERS[self.os][self.server][0])
        else:
            # if we have specified epics version then set it
            self.set_epics(epics)
            if server is None:
                # set server from epics
                self.server = default_server()
                if self.epics() not in BUILD_SERVERS[self.os][self.server]:
                    servers = epics_servers(self.os, self.epics())
                    assert servers, \
                        "No %s build servers exist for epics version %s" % \
                        (self.os, self.epics())
                    self.server = servers[0]
            else:
                # set specified server
                self.server = server

        assert self.server in BUILD_SERVERS[self.os].keys(), \
            "No build server for this OS server: %s" % self.server
        assert self.epics() in BUILD_SERVERS[self.os][self.server], \
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
        return BUILD_SERVERS

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

    def script_utils_template_file(self):
        """Returns the file system path to the script utility template for the relevant OS"""
        return os.path.join(build_scripts, self.os, "utils_template" + self.exten)

    def _script(self, params, header, format):
        """Returns the build script with headers and variables defined"""
        script = header+"\n\n"

        for name in params.keys():
            script += format % ("_" + name, params[name]+"\n")

        try:
            with open(self.script_utils_template_file(), 'r') as f:
                # skip the first line with the bin/bash
                script += "".join(f.readlines()[1:])
        except IOError:
            # No all platforms have a utils_template and thats ok...
            log.debug("No utils_template script found in: {}".format(self.script_utils_template_file()))

        with open(self.script_file(), 'r') as f:
            # skip the first line with the bin/bash
            script += "".join(f.readlines()[1:])

        return script

    def build_name(self, build, module, version):
        return "_".join([
            build, time.strftime("%Y%m%d-%H%M%S"),
            self.user, self.area, module.replace("/", "_"), version])

    def build_params(self, build_dir, module, version, vcs, build_name):

        param_dict = {
            "email"                 : self.email,
            "user"                  : self.user,
            "epics"                 : self.dls_env.epicsVer(),
            "build_dir"             : build_dir,
            "module"                : module,
            "version"               : version,
            "area"                  : self.area,
            "force"                 : "true" if self.force else "false",
            "build_name"            : build_name,
            "dls_syslog_server"     : SYSLOG_SERVER,
            "dls_syslog_server_port": SYSLOG_SERVER_PORT
        }
        if vcs is not None:
            vcs_key = '{}_dir'.format(vcs.vcs_type)
            param_dict[vcs_key] = vcs.release_repo

        return param_dict

    def local_test_possible(self):
        """Returns True if a local test build is possible"""
        local = default_server()
        remote = self.get_server()
        return local == remote

    def test(self, module, version, vcs):
        """Builds module version on the local system using the code in the
        src_dir directory of subversion."""

        build_name = self.build_name("local", module, version)
        build_dir = os.path.join(
            DLSBUILD_ROOT_DIR, "work", "etc", "build", "test", build_name)

        usermsg.info("Test build of module in {}".format(build_dir))

        params = self.build_params(
            build_dir, module, version, vcs, build_name)

        dirname = tempfile.mkdtemp(suffix="_" + module.replace("/", "_"))
        filename = os.path.join(dirname, build_name+self.exten)
        usermsg.info("Got build file {filename} to build module in {build_dir}"
                     .format(filename=filename, build_dir=build_dir))
        log.info("Local test-build parameters: {}".format(params))
        with open(filename, "w") as f:
            f.write(self.build_script(params))

        os.chmod(filename, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)

        usermsg.info("Created build file {filename} to build module in {build_dir}"
                     .format(filename=filename,build_dir=build_dir))
        usermsg.info("Performing local test build...")

        command = "/bin/env -i "
        keys = [k for k in os.environ.keys() if k.startswith("SSH")]
        for k in keys:  # Ensure SSH environment variables are passed to call
            command += "%s='%s' " % (k, os.environ[k])
        command += filename
        status = subprocess.call(command, shell=True)

        if status != 0:
            usermsg.info("Local test build failed. Results are in {}".format(build_dir))
        else:
            usermsg.info("Local test build succeeded")
            #shutil.rmtree(build_dir)
        return status

    def submit(self, module, version, vcs, test=False):
        """Submit a job to the build queue to build module version using the
        code in the src_dir directory of subversion. If test is anything
        that evaluates to True it is built in the test directory. Otherwise it
        is a normal production build."""

        build_name = self.build_name("build", module, version)
        if test:
            build_dir = os.path.join(
                DLSBUILD_ROOT_DIR, "work", "etc", "build", "test", build_name)
        else:
            build_dir = self.dls_env.prodArea(self.area)

        params = self.build_params(
            build_dir, module, version, vcs, build_name)

        # generate the filename
        pathname = os.path.join(DLSBUILD_ROOT_DIR, "work", "etc", "build", "queue")
        filename = "%s.%s" % (params["build_name"], self.server)

        # Submit the build script
        log.info("Build server job parameters: {}".format(params))
        with open(os.path.join(pathname, filename), "w") as f:
            f.write(self.build_script(params))

        # Create a log of the build
        with open(os.path.expanduser(os.path.join("~", ".dls-release-log")), "a") as f:
            f.write("\t".join([
                params["build_dir"], params["module"], params["version"],
                params["build_name"], self.server]) + "\n")

        usermsg.info("Build request file: {fname}\nCreated in : {dirname}".format(fname=filename, dirname=pathname))


class WindowsBuild(Builder):
    """Implements the build class for Windows"""
    def __init__(self, server, epics):
        Builder.__init__(self, "Windows", server, epics)
        self.exten = ".bat"

    def build_script(self, params):
        for name in params.keys():
            if params[name][:1] == "/":
                params[name] = params[name].replace(DLSBUILD_ROOT_DIR, DLSBUILD_WIN_ROOT_DIR)
        params["make"] = "make"

        return Builder._script(self, params, "@echo on", "set %s=%s")


class RedhatBuild(Builder):
    """Implements the build class for Red Hat"""
    def __init__(self, server, epics):
        Builder.__init__(self, "Linux", server, epics)
        self.exten = ".sh"

    def build_script(self, params):
        return Builder._script(self, params, "#!/bin/bash", "%s=%s")


class ArchiveBuild(RedhatBuild):
    """Implements the build class for archiving or de-archiving modules. The
    constructor takes a single parameter which, if true, dearchives, otherwise
    the module will be archived."""
    def __init__(self, server, epics, untar):
        RedhatBuild.__init__(self, server, epics)
        self.exten = ".sh"
        self.action = "unarchive" if untar else "archive"

    def build_script(self, params):
        params["action"] = self.action
        return Builder._script(self, params, "#!/bin/bash", "%s=%s")

    def script_file(self):
        return os.path.join(build_scripts, self.os, "archive.sh")

