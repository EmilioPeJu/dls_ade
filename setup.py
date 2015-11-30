from setuptools import setup

# these lines allow the version to be specified in Makefile.private
import os
version = os.environ.get("MODULEVER", "0.0")

setup(
    # name of the module
    name = "dls_ade",
    # version: over-ridden by the release script
    version = version,
    description = 'DLS Controls Group Application Development Environment scripts',
    author = 'Diamond Light Source Controls Group',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7',
    ],
    license='APACHE',
    install_requires = ['GitPython==1.0.1', 'python-ldap==2.4.22', 'six'],
    packages = ["dls_ade","dls_environment"],
    package_data = {},
    # define console_scripts
    entry_points = { 'console_scripts':
                         ['dls-release.py = dls_ade.dls_release:main',] },
    include_package_data=True,
    tests_require=['nose', 'mock'],
    test_suite='nose.collector',

    zip_safe = False
    )
