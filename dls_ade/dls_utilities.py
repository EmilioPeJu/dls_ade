import ldap
import logging
import os
import re

from packaging import version

from dls_ade.constants import LDAP_SERVER_URL
from dls_ade.exceptions import FedIdError, ParsingError



GIT_ROOT_DIR = os.getenv('GIT_ROOT_DIR', "controls")
log = logging.getLogger(__name__)


def remove_end_slash(path_string):

    if path_string and path_string.endswith('/'):
        path_string = path_string[:-1]

    return path_string


def remove_git_at_end(path_string):

    if path_string and path_string.endswith('.git'):
        return path_string[:-4]

    return path_string


def check_technical_area(area, module):
    """
    Checks if given area is IOC and if so, checks that the technical area is
    also provided.

    Args:
        area(str): Area of repository
        module(str): Module to check

    Raises:
        ParsingError if there is no technical area for a beamline

    """

    if area == "ioc" and len(module.split('/')) < 2:
        raise ParsingError("Missing technical area under beamline")


def check_tag_is_valid(tag, area=None):
    """
    Checks if a given tag is a valid tag.

    The traditional Diamond versioning is something like X-Y[-Z][dlsA[-B]]

    For Python 3 we are allowing any versions as permitted by PEP-440:

    https://www.python.org/dev/peps/pep-0440/

    Args:
        tag(str): proposed tag string
        area(str): area to check tag against

    Returns:
        bool: True if tag is valid, False if not

    """
    if area == 'python3':
        # VERBOSE allows you to ignore the comments in VERSION_PATTERN.
        check = re.compile(r"^{}$".format(version.VERSION_PATTERN), re.VERBOSE)
        result = check.search(tag)
    else:
        number = "[0-9]+"
        optional_number = "[0-9]*"

        regex_pieces = dict(
            u_v_w = "{u}\-{v}(\-{w})?".format(u=number, v=number, w=number),
            dls_x_y = "(dls{x}(\-{y})?)?".format(x=number, y=number),
            alpha_beta_z = "((alpha|beta){z})?".format(z=optional_number)
        )
        pattern = '^{u_v_w}{dls_x_y}{alpha_beta_z}$'.format(**regex_pieces)
        check = re.compile(pattern)
        result = check.match(tag)

    if result is None:
        return False

    return True


def lookup_contact_details(fed_id):
    """
    Perform an LDAP search to find details corresponding to a FED-ID.

    Args:
        fed_id(str): FED-ID to search for

    Returns:
        tuple(str, str): Contact name, email address

    Raises: FedIdError if the fed_id cannot be found in LDAP

    """

    # Set up ldap search parameters
    l = ldap.initialize(LDAP_SERVER_URL)
    basedn = "dc=fed,dc=cclrc,dc=ac,dc=uk"
    search_filter = "(&(cn={}))".format(fed_id)
    search_attribute = ["givenName", "sn", "mail"]
    search_scope = ldap.SCOPE_SUBTREE

    # Perform search, print message so user knows where program hangs
    # The lookup can hang at l.result() if the FED-ID does not exist.
    log.debug("Performing search for {}".format(fed_id))
    l.simple_bind_s()
    ldap_result_id = l.search(basedn, search_scope, search_filter,
                              search_attribute)
    ldap_output = l.result(ldap_result_id, 0)
    log.debug(ldap_output)
    # ldap_output has the form:
    # (100, [('CN=<FED-ID>,OU=DLS,DC=fed,DC=cclrc,DC=ac,DC=uk',
    # {'givenName': ['<FirstName>'], 'sn': ['<Surname>']})])

    if ldap_output[0] == 115:
        # If the FED-ID does not exist, ldap_output will look like:
        # (115, [(None,
        # ['ldap://res02.fed.cclrc.ac.uk/DC=res02,DC=fed,DC=cclrc,DC=ac,DC=uk'])])
        raise FedIdError("\"{}\" is not a FedID in LDAP".format(fed_id))

    # Extract contact name from output
    name_info_dict = ldap_output[1][0][1]
    first_name = name_info_dict['givenName'][0].decode('utf-8')
    surname = name_info_dict['sn'][0].decode('utf-8')
    email_address = name_info_dict['mail'][0].decode('utf-8')
    # name_info_dict: {'givenName': ['<FirstName>'], 'sn': ['<Surname>']}

    return '{} {}'.format(first_name, surname), email_address
