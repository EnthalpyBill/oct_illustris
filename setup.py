# Licensed under MIT License - see LICENSE

from setuptools import setup, find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name = 'oct_illustris',
    packages = find_packages(),
    version = '0.0.dev',
    url = "https://github.com/EnthalpyBill/oct_illustris",
    license = "MIT",
    author = "Bill Chen <ybchen@umich.edu>",
    maintainer = "Bill Chen <ybchen@umich.edu>",
    description = "A toolkit to quickly load Illustris with minimal cost.",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    install_requires = ["numpy>=1.18", "h5py>=2.10"],
    python_requires = ">=3.8",
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)