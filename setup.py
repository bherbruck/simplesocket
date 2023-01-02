# pylint: disable=missing-docstring, invalid-name, line-too-long

import setuptools


setuptools.setup(
    name="simplesocket",
    version="0.0.1",
    author="bherbruck",
    description="An super simple experimental tcp duplex communication library written in python.",
    url="https://github.com/bherbruck/simplesocket",
    package_dir={"": "./src"},
    entry_points={"console_scripts": ["simplesocket = simplesocket.__main__:main"]},
)
