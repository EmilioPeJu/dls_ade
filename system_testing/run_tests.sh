#! /bin/bash

echo "Running changes_since_release test ..."
python -m nose changes_since_release

echo "Running checkout_module test ..."
python -m nose checkout_module

echo "Running list_branches test ..."
python -m nose list_branches

echo "Running list_modules test ..."
python -m nose list_modules

echo "Running list_releases test ..."
python -m nose list_releases

echo "Running logs_since_release test ..."
python -m nose logs_since_release

echo "Running module_contacts test ..."
python -m nose module_contacts

echo "Running tar_module test ..."
python -m nose tar_module

cd start_new_module
echo "Running start_new_module tests ..."
python -m nose start_new_module
cd ..