import re
from dls_ade.exceptions import ParsingError
from dls_ade.vcs_git import create_tag_and_push


def check_tag_is_valid(tag):
    """
    Checks if a given tag is a valid tag.

    Args:
        tag(str): proposed tag string

    Raises:
        :class:`exceptions.ParsingError`: Invalid tag format

    """

    check = re.compile('[0-9]+\-[0-9]+(\-[0-9]+)?(dls[0-9]+(\-[0-9]+)?)?')
    result = check.match(tag)

    if result is None:
        raise ParsingError("Invalid tag " + tag)

    if result.group() != tag:
        raise ParsingError("Invalid tag " + tag)


def tag_commit(repo, tag, commit_ref):
    """
    Creates a tag in the local repository.
    Pushes this tag to the remote.
    """

    create_tag_and_push(repo, tag, commit_ref)
