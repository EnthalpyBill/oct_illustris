# -*- coding: utf-8 -*-
# Copyright (c) 2021 Bill Chen
# License: MIT (see LICENSE)

from setuptools import setup, find_packages

long_description = (
    "`mesh_illustris` is a toolkit for analyzing "
    "[Illustris](https://www.illustris-project.org/) "
    "(and also [IllustrisTNG](https://www.tng-project.org/)) "
    "data with mesh. The goal of `mesh_illustris` is to "
    "**quickly** load a subset (e.g., a box or sphere) of "
    "particles/cells with **minimal** amount of memory. "
    "Documentation is now available at "
    "[Read the Docs](https://mesh-illustris.readthedocs.io)!")

setup(
    name = 'mesh_illustris',
    packages = find_packages(),
    version = '0.2',
    url = "https://github.com/EnthalpyBill/mesh_illustris",
    license = "MIT",
    author = "Bill Chen <ybchen@umich.edu>",
    maintainer = "Bill Chen <ybchen@umich.edu>",
    description = "Load Illustris with mesh.",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    install_requires = ["numpy>=1.18", "h5py>=2.10", "numba>=0.50"],
    python_requires = ">=3.8",
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)