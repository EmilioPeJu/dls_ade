.. _system-testing-snm:

===============================
Start New Module System Testing
===============================

Contents:
---------
- :ref:`snm-systest-overview`
- :ref:`snm-comparison-files-creation`
- :ref:`necessary-server-repositories`
- :ref:`snm-systest-descriptions`
    * :ref:`name-verification-tests`
    * :ref:`local-verification-tests`
    * :ref:`local-repository-tests`
    * :ref:`remote-verification-tests`
    * :ref:`remote-repository-tests`

.. _snm-systest-overview:

Overview
----------------------------------------

The code for start_new_module system testing is stored in the start_new_module folder inside the system_testing folder.

This uses the method outlined in :ref:`general-overview`. For the start_new_module system testing, there are a number of common additional features.

First of all, a lot of the functions are affected by either the existence of local folders or whether or not the current working directory is located inside a git repository. The testing is therefore performed in a temporary directory.

Additionally, in order to determine if a particular module has been created properly, we use a tarball containing a number of folders to compare against. The construction of these folders is described in more detail in :ref:`snm-comparison-files-creation`.

.. _snm-comparison-files-creation:

Comparison Files Creation
------------------------------------------

Originally, the comparison files were generated using the original svn scripts, plus a .gitignore file (not created by svn scripts for obvious reasons).

However, as some of the templates have been modified, the comparison files are now different for the python and tools modules. Whitespace and some deprecated code has been changed for these. 

While support modules were altered to include .keep files so git would store otherwise empty folders, these are not included in the comparison files, and the system testing framework will not test for them as we are only interested in the folder structure.

The comparison files are in a tarball which is unpacked in the testing location. Just type

.. code:: bash

  tar -xzvf comparison_files.tar.gz

to unpack, and

.. code:: bash

  tar -czvf comparison_files.tar.gz comparison_files/

to recreate the tarball.

As some of the modules contain the user-specific login name, these are replaced with "USER_LOGIN_NAME" for the comparison files. After the tarball is extracted into the temporary directory, this is replaced with the user's correct login for comparison.

Look at the individual tests described in :ref:`snm-systest-descriptions` to find out what each folder is used to test for and the command used to create it.

.. _snm-systest-descriptions:

Test Descriptions
-----------------------------------------

While the individual tests are documented in their respective group python module (see below), their general behaviour (and any tricky details) are described here.

The description for each test is given in the settings dictionary (under 'description'), given as a long test name similar to unit tests.

.. _name-verification-tests:

Name Verification Tests
~~~~~~~~~~~~~~~~~~~~~~~

Located in `name_verification_tests.py`.

These test whether the name validation in the get_module_creator module works properly. They run the script with module names that are expected to fail with a 'ParsingError'. They are always run in 'no-import' mode, so the module will never export to the server if a test fails.

As a sanity check, the script tests to make sure there are no created folders at the end.

.. _local-verification-tests:

Local Verification Tests
~~~~~~~~~~~~~~~~~~~~~~~~

Located in `local_verification_tests.py`.

These test whether a module will fail to get created if a local directory conflicts with the module path for the new module, or if the current working directory is currently inside a git repository.

.. _local-repository-tests:

Local Repository Tests
~~~~~~~~~~~~~~~~~~~~~~

Located in `local_repository_tests.py`.

These test whether the different module types are created correctly, through a comparison with the comparison files discussed in :ref:`snm-comparison-files-creation`.

It goes through the complete set of creation operations, including the 'AddAppToModule' code, where an app is added to a previously existing module.

A wide variety of names are used for IOC modules as well, checking that the parsing works correctly.

For 'AddAppToModule', it adds to a previously existing repository (see :ref:`necessary-server-repositories`). 

.. _remote-verification-tests:

Remote Verification Tests
~~~~~~~~~~~~~~~~~~~~~~~~~

Located in `remote_verification_tests.py`.

These test whether the server-related verification works. This only includes two tests, for repository and app-name clashes.

The two tests require remote repositories to already exist on the server, see :ref:`necessary-server-repositories` for more details.


.. _remote-repository-tests:

Remote Repository Tests
~~~~~~~~~~~~~~~~~~~~~~~

Located in `remote_repository_tests.py`.

These test whether the different modules are correctly created and exported to the server. Similar to :ref:`local-repository-tests`, these two are then compared with comparison files as discussed in :ref:`snm-comparison-files-creation`.

For the most part, these are a reduced subset of the :ref:`local-repository-tests`, but taking only one module of each type (tools, python, support, IOC, IOC-BL (gui)).

Additionally, an 'AddAppToModule' test is also performed, but only with non-conflicting app-names.

For 'AddAppToModule', it adds to a previously existing repository (see :ref:`necessary-server-repositories`).

.. _necessary-server-repositories:

Necessary Server Repositories
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The system_testing/start_new_module/necessary_server_repos folder contains all the server repositories required by systems testing, in a tarball. The usage.txt file details their respective test module and use.

The filepaths given are absolute.
