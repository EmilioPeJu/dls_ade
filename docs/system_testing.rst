.. _system-testing-overview:

==============
System Testing
==============

Contents:
---------
- :ref:`general-overview`
- :ref:`settings-descriptions`
- :ref:`setting-up-environment`
- :ref:`test-descriptions`
    * :ref:`system-testing-snm`
    * :ref:`all-other-system-testing`
    
.. _general-overview:

General overview
----------------

Our system testing framework uses nosetests to automatically run each individual system test. This allows us to use functions such as 'setup_module' and 'teardown_module', in a similar way to that used in unit testing.

With nosetests, if a "test\_" generator is called, nosetests will run every yielded test. In the system_testing folder, the SystemTest object represents a single system test, with the __call__ method overriden to allow it to be run by nosetests.

The SystemTest init function takes in a set of arguments which specify the script to be run, a description for nosetests and a `settings` dictionary that specifies the tests to be run after the script has been called.

The system_test module also contains a generator. This generator must be passed a script name along with the settings list, and it will extract the description and optional alternative script name from the settings dictionary. All another script has to do is pass these arguments and yield the returned values.

Each dls_ade script has a separate testing folder. These are explained in more detail in the :ref:`test-descriptions` subsection.

For a simplified set of tests, look at the `example_generator.py` script in the system_testing folder. After :ref:`setting-up-environment`, and running

.. code:: bash

  tar -xzvf test_repos.tar.gz

you should be able to perform the tests by running:

.. code:: bash

  nosetests example_generator

This will perform 5 tests on the `test_error_script.py` script, which takes arguments and varies input in a basic way. Only the fourth test should fail.

If you wish to see a simplified version of the SystemTest class, look at `example.py` in the same folder. Running

.. code:: bash

  nosetests example

will demonstrate the tests, of which half should fail.

.. _settings-descriptions:

SystemTest Settings Descriptions
--------------------------------
All provided settings are given as a {string: ...} dictionary. Unless otherwise specified, assume that the dictionary values are also strings.

.. _basic-settings:

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

.. _exception-comparison-settings:

Exception comparison settings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- exception_type
    Exception type to test for.
- exception_string
    Exception string to test for.

.. _standard-output-comparison-settings:

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

.. _attribute-comparison-settings:

Attribute comparison settings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- attributes_dict
    A dictionary of (string, string) pairs. The key represents the git 
    attribute name, the value the git attribute value. Use
    'unspecified' to represent an unset value (as git does).
- local_repo_path
    The path to a local repository. This is tested for the given attribute
    values.
- server_repo_path
    This is the server repository path. This does not include the server name.
    The repository is cloned to a local directory in order for the comparison
    to take place.
    
    Note: 
    This is the same as the path used for :ref:`folder-comparison-settings`.

.. _folder-comparison-settings:

Folder comparison settings
~~~~~~~~~~~~~~~~~~~~~~~~~~

- repo_comp_method
    This describes which comparisons ought to take place. There are three alternative settings here:
        
        - 'local_comp'
            The folders local_comp_path_one and local_comp_path_two are compared.
        - 'server_comp'
            The folders local_comp_path_one and a clone from server_repo_path are compared.
        - 'all_comp'
            Both local_comp_path_one and two are compared against a clone from server_repo_path.

- local_comp_path_one
    A relative or absolute folder path
- local_comp_path_two
    A relative or absolute folder path
- server_repo_path
    This is the server repository path. This does not include the server name.
    The repository is cloned to a local directory in order for the comparison
    to take place.
    
    Note: 
    This is the same as the path used for :ref:`attribute-comparison-settings`.

.. _branch-comparison-settings:

Branch comparison settings
~~~~~~~~~~~~~~~~~~~~~~~~~~

- branch_name
    When the server_repo_path is cloned, this specifies the branch to be
    checked out afterwards. The local_repo_path repository is also checked to
    make sure that this is its active branch.

.. _setting-up-environment:

Setting up the testing environment
----------------------------------

In order to run the tests, you must set up the testing environment appropriately. In order to do this, a bash script is provided that will change all necessary environment variables.

First, in the dls_ade repository root, run in the terminal:

.. code:: bash
  
  make clean && make install

Then, get the dls_ade repository URL, eg. /path/to/dls_ade. This should not contain the second dls_ade folder name (eg. /path/to/dls_ade/dls_ade).

In the dls_ade/system_testing folder, run in the terminal:

.. code:: bash

  source setup_testing_environment.sh /path/to/dls_ade

What this will do:

- Set the global environment variable GIT_ROOT_DIR to "controlstest". 
    GIT_ROOT_DIR specifies the 'root' of the server directory tree for the
    controls group git repositories. Normally it is simply "controls", but
    "controlstest" is a safe area for testing.

- Set the PATH environment variable to include:
    * /path/to/dls_ade/prefix/bin
        This is used to access the final python scripts to be tested.

- Set the PYTHONPATH environment variable to include:
    * /path/to/dls_ade/system_testing
        This allows nosetests to use the system_testing script.
    * /path/to/dls_ade
        This allows the system_testing module to use the vcs_git module.

The system_testing module will prevent you from running any tests if you have
not yet set the GIT_ROOT_DIR environment variable.

.. _test-descriptions:

Test Descriptions
-----------------

:ref:`system-testing-snm`

:ref:`all-other-system-testing`


