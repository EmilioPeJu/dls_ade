.. _all-other-system-testing:

========================
All Other System Testing
========================

Contents:
---------
- :ref:`changes-since-release-st`
- :ref:`checkout-module-st`
- :ref:`list-branches-st`
- :ref:`list-modules-st`
- :ref:`list-releases-st`
- :ref:`logs-since-release-st`
- :ref:`module_contacts-st`
- :ref:`tar-module-st`


.. _changes-since-release-st:

Changes Since Release System Testing
------------------------------------

Changes since release has no arguments, but has two main outputs depending on the state of the repository, so there are two tests. One test with a repo that has had no changes since the last tag and one that has had changes. There is also a test for when no releases have been made for a module and one to make sure an exception is raised if the module does not exist.

.. _checkout-module-st:


Checkout Module System Testing
------------------------------

Checkout module has four tests; a standard checkout, a checkout with a branch change and the checkout of an entire area or ioc domain. These shouldn't be affected by any other test because the check is to simply compare what has been checked out to what is on the repo.

.. _list-branches-st:


List Branches System Testing
----------------------------

List branches just has one test as only has one function, all that changes is the source path given to it. This test uses dls_testpythonmod2, which should not have any changes made to it.

.. _list-modules-st:


List Modules System Testing
---------------------------

List modules has one test for an area and one test for listing an ioc domain, as the implementation for that is slightly different. These tests use a mock repository folder nested in the targetOS area. This should not be changed, or these tests will fail.

.. _list-releases-st:


List Releases System Testing
----------------------------

List releases has four arguments giving six useful functions, so there is a test for each of these. Listing releases for a module on the repo, with and without the latest flag. Listing releases for a module in prod with default and non-default epics version, with and without the latest flag.

.. _logs-since-release-st:


Logs Since Release System Testing
---------------------------------

Logs since release has three optional mutually exclusive arguments, releases, earlier and later, plus two optional flags, verbose and raw. The raw and coloured output is the same when read in by the systems test framework, so the raw flag is not tested separately. This leads to eight test in total. Default (all logs for a module) and the three range arguments, each with and without the verbose flag.

.. _module_contacts-st:


Module Contacts System Testing
------------------------------

Module contacts has four main functions, reading contacts in default and CSV format and setting contacts manually or with a CSV file. There are two tests for checking contacts, with default and CSV format. There are choices and two methods for setting contacts, setting both and setting one but leaving the other unchanged for both the manual and import methods giving six tests and eight in total. The state of the repo is reset after each test.

.. _tar-module-st:


Tar Module System Testing
-------------------------

Tar module has two main functions, tar and untar, with an epics version flag that just changes the file path to the module. There are two tests that operate on a dummy module in the support area of prod. These tests must be run together in the right order to pass, as the module itself is the only way to reset the changes.