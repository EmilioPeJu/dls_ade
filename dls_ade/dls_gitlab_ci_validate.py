#!/bin/env dls-python
"""
Open a Gitlab CI file for reading and pass it to the API for validation.
Report validation outcome.
"""
import logging
import argparse
import os
from gitlab import Gitlab
from gitlab.exceptions import GitlabVerifyError

from dls_ade import logconfig
from dls_ade.gitlabserver import GITLAB_API_VERSION, GITLAB_API_URL


usage = """
Given the path to a .gitlab-ci.yml configuration file for
Gitlab CI, pass its contents to be validated by Gitlab and output the results.

The validation will check the syntax and that any includes from public projects
are correct. It can't check local includes because it does not run in the
context of a particular project.

Validation in the context of a project can be done with the online Lint tool,
accessible from a project's menu: CI/CD > Pipelines > CI Lint.
"""


def parse_args():
    parser = argparse.ArgumentParser(
        description=usage,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    default_ci_file_path = os.path.join(
        os.getcwd(),
        ".gitlab-ci.yml"
    )

    parser.add_argument("ci_file_path", nargs="?",
                        help="Path to Gitlab CI configuration file. Default "
                             "is .gitlab-ci.yml from the current working "
                             "directory.",
                        default=default_ci_file_path)
    return parser.parse_args()


def read_file_contents(input_file_path):
    """
    Read the whole file into a string
    Args:
        input_file_path: Path to input file

    Returns:

    """
    with open(input_file_path, "r") as input_file:
        return input_file.read()


def validate(ci_file_contents):
    """
    Call the lint method from the gitlab API which sends the file contents
    off to the server to be validated.

    Args:
        ci_file_contents(str): Contents of the CI file

    Returns:
        tuple: (valid(bool), errors(list))
                errors contains a list of errors found if valid is False
    """
    gitlab_api = Gitlab(
        GITLAB_API_URL,
        api_version=GITLAB_API_VERSION,
    )
    return gitlab_api.lint(ci_file_contents)


def _main():
    # Set up loggers
    log = logging.getLogger(name="dls_ade")
    usermsg = logging.getLogger(name="usermessages")
    output = logging.getLogger(name="output")

    # Get input file path
    args = parse_args()
    ci_file_path = args.ci_file_path
    log.debug("Input file path: %s", ci_file_path)

    # Check file exists
    if not os.path.isfile(ci_file_path):
        usermsg.error("Input file %s not found", ci_file_path)
        exit(1)

    # Read whole file into string
    try:
        ci_file_contents = read_file_contents(ci_file_path)
    except IOError as e:
        usermsg.error("Input file %s not readable", ci_file_path)
        exit(1)

    # Validate file contents
    try:
        valid, errors = validate(ci_file_contents)
        if valid:
            unicode_tick = u"\u2713"
            usermsg.info(u"File PASSED validation {}".format(unicode_tick))
        else:
            usermsg.error("File FAILED validation. Errors reported:\n")
            for error in errors:
                usermsg.error("- %s", error)
            exit(1)
    except GitlabVerifyError as e:
        usermsg.error("Validation couldn't be completed.\n%s", e)
        exit(1)


def main():
    # Catch unhandled exceptions and ensure they're logged
    try:
        logconfig.setup_logging(application='dls-gitlab-ci-validate.py')
        _main()
    except Exception as e:
        logging.exception(e)
        logging.getLogger("usermessages").exception(
            "ABORT: Unhandled exception (see trace below): {}".format(e)
        )
        exit(1)
