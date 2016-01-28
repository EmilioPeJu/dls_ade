from pkg_resources import require
require('nose')

import os
import tarfile
import subprocess

COMPARISON_FILES = "comparison_files"


def find_and_replace_characters_in_folder(find, replace_with, folder):
    # Swap instances of 'find' to 'replace_with'
    subprocess.check_call(("find " + folder + " -type f -exec sed -i s/" +
                          find + "/" + replace_with + "/g {} +").split())


def untar_comparison_files_and_insert_user_login(tar_path, extract_path):

    with tarfile.open(tar_path) as tar:
        tar.extractall(extract_path)

    current_login = os.getlogin()

    find_and_replace_characters_in_folder("USER_LOGIN_NAME", current_login,
                                          extract_path)
