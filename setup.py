from distutils.core import setup
import os

# this line allows the version to be specified in the release script
globals().setdefault('version', '0.0')

scripts = ['release','changes_since_release','list_releases',"sync_from_trunk",\
           "checkout_module","vendor_import","logs_since_release",\
           "start_bugfix_branch","vendor_update","list_branches",\
           "start_feature_branch","list_modules","start_new_module",\
           "module_contacts","cs_publish","get_vendor_current","make_etc_dir",\
           "make_builder"]


# find our scripts
script_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "scripts"))
scripts = [os.path.join(script_dir, x) for x in os.listdir(script_dir) if x.endswith(".py")]


setup(
    # name of the module
    name = "dls_scripts",
    # version: over-ridden by the release script
    version = version,
    packages = ["dls_scripts"],
    # define console_scripts
    scripts = scripts,
    )
