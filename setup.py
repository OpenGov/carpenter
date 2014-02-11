import os
import glob
import shutil
from setuptools import setup

def read(fname):
    # Utility function to read the README file.
    with open(os.path.join(os.path.dirname(__file__), fname)) as fhandle:
        return fhandle.read()

# Cleanup builds so changes don't persist into setup
build_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "build"))
dist_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "dist"))
if (os.path.isdir(build_dir)):
    shutil.rmtree(build_dir)
if (os.path.isdir(dist_dir)):
    shutil.rmtree(dist_dir)
    
# Taken from Python Cookbook
# http://my.safaribooksonline.com/book/programming/python/0596001673/files/pythoncook-chp-4-sect-16
# Credit: Trent Mick
def path_split_all(path):
    all_parts = []
    while True:
        parts = os.path.split(path)
        if parts[0] == path:  # sentinel for absolute paths
            all_parts.insert(0, parts[0])
            break
        elif parts[1] == path: # sentinel for relative paths
            all_parts.insert(0, parts[1])
            break
        else:
            path = parts[0]
            all_parts.insert(0, parts[1])
    return all_parts

data_types = ["*.csv", "*.xls", "*.xlsx"]
packages = ["carpenter"]
packset = set()
for extension in data_types+["__init__.py"]:
    # Any submodules in fileparser
    packset.update(".".join(path_split_all(module)[:-1]) 
                   for module in glob.glob("carpenter/*/"+extension))
packages.extend(packset)

required = [req.strip() for req in read("requirements.txt").splitlines() if req.strip()]

setup(
    name = "Carpenter",
    version = "1.0.0",
    author = "Matthew Seal",
    author_email = "mseal@opengov.us",
    description = "A utility library which repairs and analyzes tablular data",
    install_requires = required,
    package_data = { "" : data_types },
    dependency_links = ["https://github.com/OpenGov/python_data_wrap/tarball/v1.2.0#egg=pydatawrap-1.2.0"],
    packages = packages,
    test_suite = "tests",
    zip_safe = False,
    long_description=read("README.md"),
)
