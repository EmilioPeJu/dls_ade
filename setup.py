#!/bin/env python2.4
# example of a setup.py file for any dls module
from setuptools import setup, find_packages, Extension

# this line allows the version to be specified in the release script
try:
    version = version
except:
    version = "0.0"

scripts = ['release','changes_since_release','list_releases',"sync_from_trunk",\
           "checkout_module","vendor_import","logs_since_release",\
           "start_bugfix_branch","vendor_update","list_branches",\
           "start_feature_branch","list_modules","start_new_module",\
           "module_contacts","cs_publish","get_vendor_current","make_etc_dir",\
           "make_builder"]
console_scripts = ["dls-%s.py = dls.svn.%s:%s" % \
                   (x.replace("_","-"),x,x) for x in scripts]

setup(
    # install_requires allows you to import a specific version of a module 
    install_requires = ['dls.environment==1.0'],
    # setup_requires lets us use the site specific settings for installing scripts
    setup_requires = ["dls.environment==1.0"],
    # name of the module
    name = "dls.svn",
    # version: over-ridden by the release script
    version = version,
    packages = ["dls","dls.svn"],
    package_dir = {    'dls': 'dls',
                    'dls.svn': 'src'},
    namespace_packages = ['dls'],
    # define console_scripts to be 
    entry_points = {'console_scripts': console_scripts},
    zip_safe = False 
    )
