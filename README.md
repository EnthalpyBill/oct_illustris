# `oct_illustris`: Octree for Illustris

[![version](https://img.shields.io/badge/version-v0.0-brightgreen.svg?style=flat)](https://github.com/EnthalpyBill/oct_illustris)
[![license](https://img.shields.io/badge/license-MIT-blue.svg?style=flat)](LICENSE)

`oct_illustris` is a toolkit for analyzing [`Illustris`](https://www.illustris-project.org/) (and also [`IllustrisTNG`](https://www.tng-project.org/)) data with octree. The goal of `oct_illustris` is to **quickly** load a subset (e.g., a box or sphere) of particles/cells with **minimal** amount of memory.

## Table of Contents

- [Intro](#intro)
- [Install](#install)
- [Usage](#usage)
- [Contribute](#contribute)
- [Maintainers](#maintainers)
- [Cite](#cite)
- [License](#license)

## Intro

Different from simulations performed with adaptive mesh refinement (AMR) codes, `Illustris` is a **huge** suite of simulations with the moving mesh code, `AREPO`, which has data structure similar to most particle-based codes. One disadvantage of such data structures is that particles/cells (for simplicity, "particles" hereafter) are not stored according to their spatial distances, so that it is hard to explicitly find a subset of particles within a spatial region (e.g., a box or sphere), which can be easily done for AMR simulations.

To solve this, the `Illustris` group applied the `Subfind` algorithm to the simulation and store particles according to their host halos/subhalos (for simplicity, "halos" hereafter). Therefore, we can easily find a subset of particles belonging to the same halo. This method works for most cases but still fails when 
1. two halos largely overlap, 
2. there are too many "fuzz" particles which don't belong to any halo, 
3. we want to trace the evolution of a particle, but it "jumps" to another halo at some time, etc.

Therefore, we develope the `oct_illustris` toolkit to enable analyzing `Illustris` data like any AMR simulation. [Octree](https://en.wikipedia.org/wiki/Octree) is often used to partition a 3D space. Each node of an octree has either 2^3=8 children or no child. For a space distributed with particles, a standard octree requires its leaf nodes to have fixed number of particles (usually 1). If the partilcles are uniformly distributed, the efficiency to query a particle is O(log N). However, the distribution of particles in `Illustris` is largely non-uniform. The Octree can be very deep at dense regions, reducing the efficiency to O(N). Therefore, we don't allow the octree to go too deep by setting a upper limit to the height, which is 8 by default. This limits the leaf node size to order of 100 kpc, which is sufficient for most analysis.
![octree](octree.png)
*Illustration of Octree, from [Apple Developer](https://developer.apple.com/documentation/gameplaykit/gkoctree).*

## Install

The prerequisites of `oct_illustris` are 
- `python >= 3.8`
- `numpy >= 1.18`
- `h5py >= 2.10`

This is not strict: lower versions may also work (and higher versions may not work). Please [raise an issue](https://github.com/EnthalpyBill/oct_illustris/issues/new) if it doesn't work for you. Next, the `oct_illustris` package can be easily installed with `pip`:
```shell
$ pip install oct_illustris
```
Alternatively, you can `git clone` the source package from [GitHub](https://github.com/EnthalpyBill/oct_illustris):
```shell
$ git clone git://github.com/EnthalpyBill/oct_illustris.git
```
To build and install `oct_illustris`, `cd` the folder and `pip install` it:
```shell
$ cd oct_illustris/
$ pip install -e .
```
The `-e` command allows you to make changes to the code.

## Usage

To use the package, just import it as
```python
>>> import oct_illustris as oi
```
To start with, let's load the last snapshot of `Illustris-3`:
```python
>>> base = "/your/base/path/output/snapdir_099/snap_099.0.hdf5"
>>> partType = ["dm", "gas", "stars"]
>>> d = oi.load(base, pt=partType)
```
Now, a `dataset` object is created. Let's load a 100 kpc/h sphere centered at the center of simulation box:
```python
>>> fields = ["Coordinates", "Masses"]
>>> data = d.sphere("c", r=100, pt=partType, fields=fields)
```
The method `sphere()` automatically calls the `d.index` command to start a pre-indexing process if it has not been done before. Once the pre-indexing is complete, an index file will be created at `base`. It may take time to generate this index file, but once generated, `oct_illustris` will skip pre-indexing when `d.index` is called again. If you want to save the index file to a different location, just specify the location to `oi.load()` with the argument `index_fn`.

`data` is a dict storing the required fields of particles of different types. An important goal of `oct_illustris` is to keep consistancy with the original data, so that you can easily play with `data` without changing your original code. For example, lets make a projection plot along the z-axis for the 100 kpc/h sphere:
```python
>>> import matplotlib.pyplot as plt
>>> x = data["Coordinates"][:,0]
>>> y = data["Coordinates"][:,1]
>>> m = data["Masses"]
>>> plt.hist2d(x, y, weights=m)
```
The output plot looks like this:

## Contribute

Feel free to dive in! [Raise an issue](https://github.com/EnthalpyBill/oct_illustris/issues/new) or submit pull requests.

## Maintainers

**Author:** 
- [@EnthalpyBill (Bill Chen)](https://github.com/EnthalpyBill)

**Maintainers:** 
- [@EnthalpyBill (Bill Chen)](https://github.com/EnthalpyBill)

## Cite

This README file is based on the [Standard Readme](https://github.com/RichardLitt/standard-readme) project.

## License

`oct_illustris` is available at [GitHub](https://github.com/EnthalpyBill/oct_illustris) under the [MIT license](LICENSE).