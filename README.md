# `mesh_illustris`: Load Illustris with mesh

[![pypi](https://img.shields.io/pypi/v/mesh_illustris?color=blue)](https://pypi.org/project/mesh-illustris)
[![version](https://img.shields.io/badge/version-v0.2.dev-green?style=flat&logo=github)](https://github.com/ybillchen/mesh_illustris)
[![license](https://img.shields.io/github/license/ybillchen/mesh_illustris?color=blue)](LICENSE)
[![doc](https://img.shields.io/readthedocs/mesh_illustris?color=brightgreen)](https://mesh-illustris.readthedocs.io)
[![workflow](https://img.shields.io/github/actions/workflow/status/ybillchen/mesh_illustris/build_and_test.yaml?color=brightgreen&logo=github)](https://github.com/ybillchen/mesh_illustris/actions)

`mesh_illustris` is a toolkit for analyzing [Illustris](https://www.illustris-project.org/) (and also [IllustrisTNG](https://www.tng-project.org/)) data with mesh. The goal of `mesh_illustris` is to **quickly** load a subset (e.g., a box or sphere) of particles/cells with **minimal** amount of memory. [Documentation](https://mesh-illustris.readthedocs.io) is now available!

## Intro

Illustris is a **huge** suite of simulations with the moving mesh code, [`AREPO`](https://arepo-code.org/). Illustris applies the FoF and `Subfind` algorithms to identify halos/subhalos and store particles accordingly. Therefore, we can easily load a subset of particles belonging to the same halo/subhalo. This method works for most cases but still fails when 
1. two halos largely overlap, 
2. there are too many "fuzz" particles which don't belong to any halo, 
3. we want to trace the evolution of a particle, but it "jumps" to another halo at some time, etc.

Therefore, we develope the `mesh_illustris` toolkit to enable loading Illustris like mesh-based simulations. `mesh_illustris` splits the entire volume into a 3D mesh and index each particle/cell according to its location in the mesh. This method allows us to **quickly** load a subset (e.g., a box or sphere) of particles/cells with **minimal** amount of memory.

## Install

The prerequisites of `mesh_illustris` are 

```
python >= 3.8
numpy >= 1.18
h5py >= 2.10
numba >= 0.50
```

Lower versions may also work (and higher versions may not work). Please [raise an issue](https://github.com/ybillchen/mesh_illustris/issues/new) if it doesn't work for you. Next, the `mesh_illustris` package can be easily installed with `pip`:
```shell
$ pip install mesh_illustris
```
Alternatively, you can `git clone` the source package from [GitHub](https://github.com/ybillchen/mesh_illustris):
```shell
$ git clone https://github.com/ybillchen/mesh_illustris.git
```
To build and install `mesh_illustris`, `cd` the folder and `pip install` it:
```shell
$ cd mesh_illustris/
$ pip install -e .
```
The `-e` command allows you to make changes to the code.

## Usage

To use the package, just import it as
```python
>>> import mesh_illustris as mi
```
To start with, let's load the last snapshot of the simulation:
```python
>>> base = "/your/base/path/output"
>>> partType = ["gas"]
>>> d = mi.load(base, snapNum=99, partType=partType)
```
Now, a `Dataset` object is created. Let's load a 100 kpc/h box in the simulation:
```python
>>> boundary = np.array([[0,0,0],[100,100,100]])
>>> fields = ["Coordinates", "Masses"]
>>> data = d.box("c", boundary=boundary, partType=partType, fields=fields)
```
The method `box()` automatically start a pre-indexing process if it has not been done before. Once the pre-indexing is complete, several index files will be created at `base`. It may take time to generate such files, but once generated, `mesh_illustris` will skip pre-indexing for the next time. If you want to save the index file to a different location, just specify the path to `load()` with the argument `index_path`.

For more example scripts using `mesh_illustris`, please see [cookbook](https://mesh-illustris.readthedocs.io/en/latest/cookbook.html). 

## Contribute

Feel free to dive in! [Raise an issue](https://github.com/ybillchen/mesh_illustris/issues/new) or submit pull requests.

## Maintainers

**Author:** 
- [@ybillchen (Bill Chen)](https://github.com/ybillchen)

**Maintainers:** 
- [@ybillchen (Bill Chen)](https://github.com/ybillchen)

## Cite

This README file is based on [Standard Readme](https://github.com/RichardLitt/standard-readme).

## License

`mesh_illustris` is available at [GitHub](https://github.com/ybillchen/mesh_illustris) under the [MIT license](LICENSE).
