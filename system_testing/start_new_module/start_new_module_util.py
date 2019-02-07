import os
import tarfile
import subprocess


dir_path = os.path.dirname(os.path.realpath(__file__))
COMPARISON_FILES = os.path.join(dir_path, "comparison_files")


def find_and_replace_characters_in_folder(find, replace_with, folder):
    """Swap the string `find` with the string `replace_with` in `folder`.

    This search is global in the files, and recursive through the folder.

    Args:
        find: The string to search for.
        replace_with: The string that `find` is to be replaced with.
        folder: The folder which is searched.

    """
    # Swap instances of 'find' to 'replace_with'
    subprocess.check_call(("find " + folder + " -type f -exec sed -i s/" +
                          find + "/" + replace_with + "/g {} +").split())


def untar_comparison_files_and_insert_user_login(tar_path, extract_path):
    """Untar the comparison files tarball and insert the current user's name.

    The string USER_LOGIN_NAME will be replaced by the current user's login.

    Args:
        tar_path: The path to the tarball.
        extract_path: The path in which the tarball is untarred.

    """
    with tarfile.open(tar_path) as tar:
        tar.extractall(extract_path)

    current_login = os.getlogin()

    find_and_replace_characters_in_folder("USER_LOGIN_NAME", current_login,
                                          extract_path)
