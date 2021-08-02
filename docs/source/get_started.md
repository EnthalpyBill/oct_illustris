# Get started

## Install

The prerequisites of `mesh_illustris` are 

```
python >= 3.8
numpy >= 1.18
h5py >= 2.10
```

Lower versions may also work (and higher versions may not work). Please [raise an issue](https://github.com/EnthalpyBill/mesh_illustris/issues/new) if it doesn't work for you. Next, the `mesh_illustris` package can be easily installed with `pip`:
```shell
$ pip install mesh_illustris
```
Alternatively, you can `git clone` the source package from [GitHub](https://github.com/EnthalpyBill/mesh_illustris):
```shell
$ git clone https://github.com/EnthalpyBill/mesh_illustris.git
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
To start with, let's load the last snapshot of Illustris-3:
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