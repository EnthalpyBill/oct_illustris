# Test guide

Performing tests is extremely important in producing robust codes. The test framework of `mesh_illustris` is `pytest`. Since we don't need `pytest` for common use, it's not included in `install_requires` of `setup.py`. So, before moving on, please manually install `pytest` if it's not installed:
```shell
$ pip install pytest
```

There are two ways to run tests. First, we can simply run 
```shell
$ pytest
```
under the source code path of `mesh_illustris` (with `__init__.py` inside). Run `pytest -v` instead if you want more information. See [`pytest`'s documentation](https://docs.pytest.org) for more details.

The second way doesn't require `cd` the source code path. After installing `mesh_illustris`, we can run tests by
```python
>>> import mesh_illustris as mi
>>> mi.test()
```
Similarly, replace `mi.test` with `mi.test(["-v"])` if you want more information.

If you get everything passed, congratulations! Skipped cases are also OK. However, if you see errors, we'd strongly suggest you to slow down and check what's wrong with the code. [Raise an issue](https://github.com/EnthalpyBill/mesh_illustris/issues/new) if it can't be solved!