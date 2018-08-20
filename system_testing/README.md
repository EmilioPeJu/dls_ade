# DLS Application Development Environment (ADE) System Tests

A collection of system tests. For a detailed overview of the system testing framework
see [docs/system_testing_info.rst](../docs/system_testing_info.rst).

## Requirements

You must have permissions to access the controlstest area of gitolite.

You must have set up the Development Environment as described in the root README

## Setting up the testing environment

Navigate to system_testing and run

```
source setup_testing_environment.sh
```

This script will:
* setup your $PYTHONPATH appropriately
* call push_required_repos.py (which will send the repositories located in necessary_server_repos/controlstest.tar.gz to the server, for testing)

## Running the system tests

Run the tests in the system_testing/<script_name> folders individually, using 'python -m nose' or 'nosetests'.

e.g.
```
nosetests changes_since_release/
```

or

Run all tests using the run_tests.sh script

```
./run_tests.sh

```

#### Notes
* Use -v for verbose mode
* For start_new_module, specify a _tests.py file to only run that particular test group.
* If you run remote_repository_tests.py (in start_new_module), make sure you commit and push the new number stored in 'repo_test_num.txt'.
* The systemtests module itself has a test (system_testing_test.py).
