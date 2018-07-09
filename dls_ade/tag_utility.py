import re
from dls_ade.exceptions import ParsingError


def check_tag_is_valid(tag):
    """
    Checks if a given tag is avalid tag.

    Args:
        tag(str): proposed tag string

    Raises:
        :class:`exceptions.ParsingError`: Invalid tag format

    """
    check = re.compile('[0-9]+\-[0-9]+(\-[0-9]+)?(dls[0-9]+(\-[0-9]+)?)?')
    result = check.match(tag)

    if result.group() != tag:
        raise ParsingError("Invalid tag " + tag)
