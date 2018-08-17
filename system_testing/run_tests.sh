#! /bin/bash

echo "Running changes_since_release test ..."
nosetests changes_since_release

echo "Running checkout_module test ..."
nosetests checkout_module

echo "Running list_branches test ..."
nosetests list_branches

echo "Running list_modules test ..."
nosetests list_modules

echo "Running list_releases test ..."
nosetests list_releases

echo "Running logs_since_release test ..."
nosetests logs_since_release

echo "Running module_contacts test ..."
nosetests module_contacts

echo "Running tar_module test ..."
nosetests tar_module

cd start_new_module
echo "Running start_new_module tests ..."
nosetests

cd ..
