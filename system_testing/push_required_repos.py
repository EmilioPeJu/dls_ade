#! /bin/env dls-python
"""To be run at the end of setup_testing_environment.sh"""

import os

from dls_ade import Server
import tarfile
import shutil

NECESSARY_REPOS_DIR = "necessary_server_repos"
SERVER_REPOS_BASE = os.path.join(NECESSARY_REPOS_DIR, "controlstest")
TAR_LOCATION = SERVER_REPOS_BASE + ".tar.gz"


def push_repo(local_path):
    server_repo_path = local_path[len(NECESSARY_REPOS_DIR) + 1:]
    area, module = server_repo_path.split('/')[-2:]

    server = Server()
    if not server.is_server_repo(server_repo_path):
        repo = server.create_new_local_repo(module, area, local_path)
        server.create_remote_repo(server_repo_path)
        repo.push_all_branches_and_tags(server_repo_path, "systest")
        print("Pushed to server:")
    else:
        print("This repository already exists on the server:")

    print(server_repo_path)


def untar_files(tar_path, extract_path):
    """Untar the tarball into the extraction path.

    Args:
        tar_path: The path to the tarball.
        extract_path: The path in which the tarball is untarred.

    """
    with tarfile.open(tar_path) as tar:
        tar.extractall(extract_path)


if __name__ == "__main__":

    # Untar files into same directory
    untar_files(TAR_LOCATION, NECESSARY_REPOS_DIR)

    for path, dirs, files in os.walk(SERVER_REPOS_BASE, topdown=True):
        if ".git" in dirs:
            dirs = []
            push_repo(path)

    shutil.rmtree(SERVER_REPOS_BASE)
