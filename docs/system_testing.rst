.. _system-testing:

==============
System Testing
==============

Contents:
---------
- :ref:`systest-general-overview`
- :ref:`systest-settings-descriptions`
- :ref:`systest-setting-up-environment`
- :ref:`systest-test-descriptions`

    * :ref:`system-testing-snm`
    * :ref:`all-other-system-testing`
    
.. _systest-general-overview:

General overview
----------------

Our system testing framework uses nosetests to automatically run each
individual system test. This allows us to use functions such as 'setup_module'
and 'teardown_module', in a similar way to that used in unit testing.

With nosetests, if a "test\_" generator is called, nosetests will run every
yielded test. In the system_testing folder, the SystemTest object represents a
single system test, with the __call__ method overriden to allow it to be run by
nosetests.

The SystemTest init function takes in a set of arguments which specify the
script to be run, a description for nosetests and a `settings` dictionary that
specifies the tests to be run after the script has been called.

The system_test module also contains a generator. This generator must be
passed a script name along with the settings list, and it will extract the
description and optional alternative script name from the settings dictionary.
All another script has to do is pass these arguments and yield the returned
values.

Each dls_ade script has a separate testing folder. These are explained in more
detail in the :ref:`systest-test-descriptions` subsection.

To run a particular test, run

.. code:: bash

  nosetests module_system_test.py -v

in the test's directory. The '-v' command is optional, but will show the name
of each test as it is run.

For a simplified set of tests, look at the `example_generator.py` script in the
system_testing folder. After :ref:`systest-setting-up-environment`, and running

.. code:: bash

  tar -xzvf test_repos.tar.gz

you should be able to perform the tests by running:

.. code:: bash

  nosetests example_generator

This will perform 5 tests on the `test_error_script.py` script, which takes
arguments and varies input in a basic way. Only the fourth test should fail.

If you wish to see a simplified version of the SystemTest class, look at
`example.py` in the same folder. Running

.. code:: bash

  nosetests example

will demonstrate the tests, of which half should fail.

.. _systest-setting-up-environment:

Setting up the testing environment
----------------------------------

In order to run the tests, you must set up the testing environment
appropriately. In order to do this, a bash script is provided that will change
all necessary environment variables, as well as push all the required
repositories to the server.

First, in the dls_ade repository root, run in the terminal:

.. code:: bash

  make clean && make install

For the environment variables, you need three paths:

1. The path to the bin folder.
    These are the executables that are run by the end user. From the root of
    the repository, this is `prefix/bin`.

2. The path to the python library egg.
    From the root of the repository, this is
    `prefix/lib/pythonx.x/site-packages/dls_ade-y.y-pyx.x.egg`, where `x`
    varies depending on python or dls_ade version numbers.

3. The path to the system_testing folder.
    From the root of the repository, this is just `system_testing`

To get the absolute path, use:

.. code:: bash

  readlink -f relative/path/to/folder

In the dls_ade/system_testing folder, run in the terminal:

.. code:: bash

  source setup_testing_environment.sh /path/to/bin /path/to/egg /path/to/system_testing

What this script will do:

- Set the global environment variable GIT_ROOT_DIR to "controlstest".
    GIT_ROOT_DIR specifies the 'root' of the server directory tree for the
    controls group git repositories. Normally it is simply "controls", but
    "controlstest" is a safe area for testing.

- Set the PATH environment variable to include:
    * bin/ folder
        This is used to access the final python scripts to be tested.

- Set the PYTHONPATH environment variable to include:
    * system_testing folder
        This allows us to use the system_testing module.
    * library egg folder
        This allows the scripts in bin/, as well as the system_testing module,
        to access the dls_ade modules.

- Upload the repositories in `necessary_server_repos/controlstest.tar.gz`.
    These are uploaded to the server, for use by system test scripts. A
    repository is not exported if it already exists on the server. See
    :ref:`systest-auto-export` for more details.

The system_testing module will prevent you from running any tests if you have
not yet set the GIT_ROOT_DIR environment variable (performed by the setup
script).

.. _systest-auto-export:

Automatic Export of Repositories
--------------------------------

The tarball `system_testing/necessary_server_repos/controlstest.tar.gz` stores
a folder named `controlstest` that contains a number of git repositories. These
are uploaded for system testing.

In the `necessary_server_repos` folder is a text file, `repo_list.txt`. This is
a list of all the repositories in the tarball, given by their path relative to
the `controlstest` folder. Underneath each entry is a list of system tests
where it is used, along with a brief description of its purpose.

These repositories are uploaded to the server, using their relative file paths
to determine their server location. For example, a repository located in
`controlstest/support/test_support_module` will be uploaded to the server with
`controlstest/support/test_support_module` as a path. It will not find
repositories that are nested inside another repository.

All local branches and tags will be pushed by this function. If you clone down
a server repository with multiple branches and tags, the tags are downloaded
automatically but only the `master` branch is cloned. As a result, this script
will only push the master branch along with all the tags.

To allow additional branches to be exported when using this script, checkout
the remote branch `branch_name` using

.. code:: bash

  git checkout -b branch_name origin/branch_name

assuming the remote name is origin.

To edit the repositories, simply untar them:

.. code:: bash

  tar -xzvf controlstest.tar.gz

Add or edit your repository, and tar them back up again:

.. code:: bash

  tar -czvf controlstest.tar.gz controlstest/

.. _systest-settings-descriptions:

SystemTest Settings Descriptions
--------------------------------
All provided settings are given as a {string: ...} dictionary. Unless
otherwise specified, assume that the dictionary values are also strings.

.. _systest-basic-settings:

Basic settings
~~~~~~~~~~~~~~
These two settings handle the running of the script.

- arguments
    Arguments to be provided to the script.
- input
    Input to be provided to the called process. 
    
    If not set, no input is provided. If the string given is blank (""), then 
    the process will still register the input (as though pressing Enter without
    any text).

.. _systest-server-default-settings:

Server default settings
~~~~~~~~~~~~~~~~~~~~~~~
This enables the user to set the server repository to a 'default' state before
running the script.

- default_server_repo_path
    The 'server_repo_path' is overwritten by this repository's contents. This
    means any commit history etc. is deleted.

.. _systest-exception-comparison-settings:

Exception comparison settings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- exception_type
    Exception type to test for.
- exception_string
    Exception string to test for.

.. _systest-standard-output-comparison-settings:

Standard output comparison setttings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The standard output obtained is entirely separate from the standard error. As a
result, logging messages do not interfere with these tests.

- std_out_compare_string
    A string which is compared against the entirety of the output.
- std_out_starts_with_string
    A string which is compared against only the beginning of the output.
- std_out_ends_with_string
    A string which is compared against only the end of the output.

.. _systest-attribute-comparison-settings:

Attribute comparison settings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- attributes_dict
    A dictionary of (string, string) pairs. The key represents the git 
    attribute name, the value the git attribute value. Use 'unspecified' to
    represent an unset value (as git does).
- local_repo_path
    The path to a local repository. This is tested for the given attribute
    values.
- server_repo_path
    This is the server repository path. This does not include the server name.
    The repository is cloned to a local directory in order for the comparison
    to take place.
    
    Note: 
        This is the same path as used for
        :ref:`systest-folder-comparison-settings`.

.. _systest-folder-comparison-settings:

Folder comparison settings
~~~~~~~~~~~~~~~~~~~~~~~~~~

- repo_comp_method
    This describes which comparisons ought to take place. There are three
    alternative settings here:
        
        - 'local_comp'
            The folders local_comp_path_one and local_comp_path_two are
            compared.
        - 'server_comp'
            The folders local_comp_path_one and a clone from server_repo_path
            are compared.
        - 'all_comp'
            Both local_comp_path_one and two are compared against a clone from
            server_repo_path.

- local_comp_path_one
    A relative or absolute folder path
- local_comp_path_two
    A relative or absolute folder path
- server_repo_path
    This is the server repository path. This does not include the server name.
    The repository is cloned to a local directory in order for the comparison
    to take place.

    Note:
        This is the same path as used for
        :ref:`systest-attribute-comparison-settings`.

`.git`, `.gitattributes` and `.keep` folders and files are all ignored for this
comparison.



.. _systest-branch-comparison-settings:

Branch comparison settings
~~~~~~~~~~~~~~~~~~~~~~~~~~

- branch_name
    When the server_repo_path is cloned, this specifies the branch to be
    checked out afterwards. The local_repo_path repository is also checked to
    make sure that this is its active branch.

.. _systest-test-descriptions:

Test Descriptions
-----------------

:ref:`system-testing-snm`

:ref:`all-other-system-testing`


