from setuptools import setup

# these lines allow the version to be specified in Makefile.private
import os
version = os.environ.get("MODULEVER", "0.0")

# find the build scripts
savecwd = os.getcwd()
os.chdir("dls_ade")

build_scripts = []
for root, subFolders, files in os.walk("dlsbuild_scripts"):
    build_scripts += [os.path.join(root, x) for x in files if x.endswith(".bat") or x.endswith(".sh") ]

template_files = []
for root, _, files in os.walk("module_templates"):
    template_files += [os.path.join(root, x) for x in files]

additional_files = build_scripts + template_files
os.chdir(savecwd)

setup(
    # name of the module
    name="dls_ade",
    # version: over-ridden by the release script
    version=version,
    description='DLS Controls Group Application Development Environment scripts',
    author='Diamond Light Source Controls Group',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7',
    ],
    license='APACHE',
    install_requires=['GitPython==2.1.5', 'python-ldap>=2.3.12', 'six'],
    packages=["dls_ade"],
    package_data={"dls_ade": additional_files},
    # define console_scripts
    entry_points={'console_scripts':
                  ['dls-changes-since-release.py = dls_ade.dls_changes_since_release:main',
                   'dls-checkout-module.py = dls_ade.dls_checkout_module:main',
                   'dls-list-branches.py = dls_ade.dls_list_branches:main',
                   'dls-list-modules.py = dls_ade.dls_list_modules:main',
                   'dls-list-releases.py = dls_ade.dls_list_releases:main',
                   'dls-logs-since-release.py = dls_ade.dls_logs_since_release:main',
                   'dls-module-contacts.py = dls_ade.dls_module_contacts:main',
                   'dls-release.py = dls_ade.dls_release:main',
                   'dls-start-new-module.py = dls_ade.dls_start_new_module:main',
                   'dls-tar-module.py = dls_ade.dls_tar_module:main']},

    include_package_data=True,
    tests_require=['nose', 'mock'],
    test_suite='nose.collector',

    zip_safe=False
    )
