import os

# Root directory to perform build operations.
# For testing/development, this can be changed to redirect build scripts away
# from the build server, e.g. a user's home directory. Set the environment
# variables DLSBUILD_ROOT_DIR and/or DLSBUILD_WIN_ROOT_DIR to override the
# default location.
# Be sure that the root dir contains the expected directories (e.g. work/etc/build/queue).
DLSBUILD_ROOT_DIR = os.getenv("DLSBUILD_ROOT_DIR", "/dls_sw")
DLSBUILD_WIN_ROOT_DIR = os.getenv("DLSBUILD_WIN_ROOT_DIR", "W:/")

LDAP_SERVER_URL = 'ldap://altfed.cclrc.ac.uk'
GIT_ROOT = "dascgitolite@dasc-git.diamond.ac.uk"

_gelflog_server_addr = os.getenv('ADE_GELFLOG_SERVER', "graylog2.diamond.ac.uk:12201").split(':')
GELFLOG_SERVER = _gelflog_server_addr[0]
GELFLOG_SERVER_PORT = _gelflog_server_addr[1]

_syslog_server = os.getenv("ADE_SYSLOG_SERVER", "{}:12209".format(GELFLOG_SERVER)).split(':')
SYSLOG_SERVER = _syslog_server[0]
SYSLOG_SERVER_PORT = _syslog_server[1]

BUILD_SERVERS = {
    "Linux": {
        "redhat6-x86_64": ["R3.14.12.3"],
        "redhat7-x86_64": ["R3.14.12.7"],
    },
    "Windows": {
        "windows6-x86"     : ["R3.14.12.3"],
        "windows6-AMD64"   : ["R3.14.12.3"],
        "windows6_3-AMD64" : ["R3.14.12.7"],
    }
}

SERVER_SHORTCUT = {
    "6": "redhat6-x86_64",
    "7": "redhat7-x86_64",
    "32": "windows6-x86",
    "64": "windows6-AMD64",
    "64-2012": "windows6_3-AMD64",
}

