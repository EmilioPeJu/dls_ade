from setuptools import setup
from setuptools.command.build_py import build_py as setuptools_build_py

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

for root, _, files in os.walk("cookiecutter_templates"):
    template_files += [os.path.join(root, x) for x in files]

additional_files = build_scripts + template_files
os.chdir(savecwd)


class BuildPreservingPackageDataMode(setuptools_build_py):

    def build_package_data(self):
        """Copy data files into build directory"""
        # Copied from distutils
        for package, src_dir, build_dir, filenames in self.data_files:
            for filename in filenames:
                target = os.path.join(build_dir, filename)
                self.mkpath(os.path.dirname(target))
                self.copy_file(os.path.join(src_dir, filename), target,
                               preserve_mode=True)


setup(
    # name of the module
    name="dls_ade",
    cmdclass={
        'build_py': BuildPreservingPackageDataMode
    },
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
    install_requires=['GitPython==2.1.8', 'python-ldap==3.1.0', 'six==1.10.0',
                      'pygelf==0.3.1', 'cookiecutter==1.6.0',
                      'python-gitlab==1.6.0'],
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
                   'dls-tar-module.py = dls_ade.dls_tar_module:main',
                   'dls-pipfilelock-to-venv.py = dls_ade.dls_pipfilelock_to_venv:main',
                   'dls-populate-dist.py = dls_ade.dls_populate_dist:main',
                   'dls-install-packages.py = dls_ade.dls_install_packages:main']},

    include_package_data=True,
    tests_require=['nose', 'mock'],
    test_suite='nose.collector',

    zip_safe=False
    )
