# `oct_illustris`: Octree for Illustris

[![version](https://img.shields.io/badge/version-v0.0-brightgreen.svg?style=flat)](https://github.com/EnthalpyBill/oct_illustris)
[![license](https://img.shields.io/badge/license-MIT-blue.svg?style=flat)](LICENSE)

`oct_illustris` is a toolkit for analyzing [`Illustris`](https://www.illustris-project.org/) (and also [`IllustrisTNG`](https://www.tng-project.org/)) data with octree. The goal of `oct_illustris` is to **quickly** load a subset (e.g., a box or sphere) of particles/cells with **minimal** amount of memory.

## Table of Contents

- [Background](#background)
- [Installation](#installation)
- [Usage](#usage)
- [Maintainers](#maintainers)
- [License](#license)

## Background

Different from simulations performed with adaptive mesh refinement (AMR) codes, `Illustris` is a **huge** suite of simulations with the moving mesh code, `AREPO`, which has data structure similar to most particle-based codes. One disadvantage of such data structures is that particles/cells (for simplicity, "particles" hereafter) are not stored according to their spatial distances, so that it is hard to explicitly find a subset of particles within a spatial region (e.g., a box or sphere), which can be easily done for AMR simulations.

To solve this, the `Illustris` group applied the `Subfind` algorithm to the simulation and store particles according to their host halos/subhalos (for simplicity, "halos" hereafter). Therefore, we can easily find a subset of particles belonging to the same halo. This method works for most cases but still fails when 1) two halos largely overlap, 2) there are too many "fuzz" particles which does not belong to any halo, 3) we want to trace the evolution of a particle, but it "jumps" to another halo at some time, etc. Therefore, we develope the `oct_illustris` toolkit to enable analyzing `Illustris` data like any AMR simulation.

## Installation

The prerequisites of `oct_illustris` are 
```shell
numpy >= 1.18
h5py >= x.x
```
Lower versions may also work. 

## Usage

To use the package, just import it as
```python
>>> import oct_illustris as oi
```
To start with, let's load the last snapshot of `Illustris-3`:
```python
>>> base = "/your/base/path/output/snapdir_099/snap_099.0.hdf5"
>>> partType = ["dm","gas","stars","bh"]
>>> d = oi.load(base, pt=partType)
```
Now, a `dataset` object is created. Let's load a 100 kpc/h sphere centered at the center of simulation box:
```python
>>> fields = ["Coordinates","Masses"]
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

## Maintainers

Author: [@EnthalpyBill (Bill Chen)](https://github.com/EnthalpyBill)

## License

`oct_illustris` is available at [GitHub](https://github.com/EnthalpyBill/oct_illustris) under the [MIT license](LICENSE).