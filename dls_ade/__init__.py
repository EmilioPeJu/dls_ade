import sys


def bytes_to_string(bytes_obj):
    """Create a string object on both Python 2 and 3.

    Args:
        - bytes_obj: typically returned from subprocess.check_output

    Returns
        - str: on Python 2 this is bytes and on Python 3 this is unicode

    """
    if sys.version_info[0] >= 3:
        return bytes_obj.decode('utf-8')
    else:
        return bytes_obj


from dls_ade.gitlabserver import GitlabServer as Server
