# DLS Application Development Environment (ADE) System Tests

A collection of system tests. For a detailed overview of the system testing framework
see [docs/system_testing_info.rst](../docs/system_testing_info.rst).

## Requirements

You must have permissions to access the controlstest area of gitolite.

## Setting up the testing environment

Setup a virtualenv in the root of the project and install the system tests.

```
virtualenv -p /path/to/your/python2.7 venv
source venv/bin/activate
make clean
make install
```

Navigate to system_testing and run

```
source setup_testing_environment.sh <installation-prefix>
```

where `<installation-prefix>` is the location to which `dls_ade` was installed,
typically `dls_ade/prefix`.

This script will:
* setup your $PYTHONPATH appropriately
* call push_required_repos.py (which will send the repositories located in necessary_server_repos/controlstest.tar.gz to the server, for testing)


```
cd system_testing
source setup_testing_environment.sh /path/to/dls_ade/prefix
```

## Running the system tests

Run all the tests:
```
source run_tests.sh
```

Or alternatively run the tests in the system_testing/<script_name> folders individually, using 'python -m nose'.

e.g.
```
python -m nose changes_since_release/
```

#### Notes
* Use -v for verbose mode
* For start_new_module, specify a _tests.py file to only run that particular test group.
* If you run remote_repository_tests.py (in start_new_module), make sure you commit and push the new number stored in 'repo_test_num.txt'.
* The systemtests module itself has a test (system_testing_test.py).
