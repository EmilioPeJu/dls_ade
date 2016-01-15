from setuptools import setup

# these lines allow the version to be specified in Makefile.private
import os
version = os.environ.get("MODULEVER", "0.0")

# find the build scripts
savecwd=os.getcwd()
os.chdir("dls_ade")

build_scripts = []
for root, subFolders, files in os.walk("dlsbuild_scripts"):
    build_scripts += [os.path.join(root, x) for x in files if x.endswith(".bat") or x.endswith(".sh") ]

template_files = []
for root, _, files in os.walk("new_module_templates"):
    template_files += [os.path.join(root, x) for x in files]

additional_files = build_scripts + template_files
os.chdir(savecwd)

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
    install_requires = ['GitPython>=0.3.2', 'python-ldap>=2.3.12', 'six'],
    packages = ["dls_ade","dls_environment"],
    package_data = {"dls_ade": additional_files},
    # define console_scripts
    entry_points = { 'console_scripts':
                         ['dls-release.py = dls_ade.dls_release:main',] },
    include_package_data=True,
    tests_require=['nose', 'mock'],
    test_suite='nose.collector',

    zip_safe = False
    )
