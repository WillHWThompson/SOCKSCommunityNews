import sys

import setuptools
from setuptools import setup

__version__ = "0.0"

if not (3, 9) < sys.version_info < (3, 13):
    sys.exit("lcs requires Python 3.10 or 3.11.")

name = "scn_src"

version = __version__

authors = "Will Thompson and ??"

author_email = "wthomps3@uvm.edu"


def parse_requirements_file(filename):
    with open(filename) as fid:
        requires = [l.strip() for l in fid.readlines() if not l.startswith("#")]
    return requires


install_requires = parse_requirements_file("requirements.txt")

license = "3-Clause BSD license"

setup(
    name=name,
    packages=setuptools.find_packages(),
    version=version,
    author=authors,
    author_email=author_email,
    install_requires=install_requires,
)
