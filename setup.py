from setuptools import setup, find_packages

setup(
    # Application name:
    name="repofish",

    # Version number (initial):
    version="0.0.2",

    # Application author details:
    author="Vanessa Sochat",
    author_email="vsochat@stanford.edu",

    # Packages
    packages=find_packages(),

    # Data
    package_data = {'repofish.lib':['*.json']},

    # Details
    url="http://www.github.com/vsoch/repofish",

    license="LICENSE",
    description="search github repos for python functions and generate standard data structures for them",

    install_requires = ['numpy','pandas','gitpython']
)
