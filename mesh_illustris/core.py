# -*- coding: utf-8 -*-
# Copyright (c) 2021 Bill Chen
# License: MIT (see LICENSE)

"""
core codes of the mesh_illustris package.
"""

import os
import numpy as np
import h5py
import time
from multiprocessing import Pool

from .il_util import *
from .mesh import Mesh

__all__ = ["Dataset", "SingleDataset"]

class Dataset(object):
    """Dataset class stores a snapshot of simulation."""

    def __init__(self, datasets, n_chunk, parallel=True, Np=32):
        """
        Args:
            datasets (list of SingleDataset): Chunks that store the 
                snapshot of simulation. 
            n_chunk (int): Number of chunks.
            parallel (bool, default to False): Parallel or not.
            Np (int, default to 32): Number of processes.
        """

        super(Dataset, self).__init__()
        self._datasets = datasets
        self._n_chunk = n_chunk
        self._parallel = parallel
        self._Np = Np

    @property
    def datasets(self):
        """list of SingleDataset: Chunks that store the snapshot 
            of simulation."""
        return self._datasets

    @property
    def n_chunk(self):
        """int: Number of chunks."""
        return self._n_chunk

    def _combine(self, func, partType, fields, mdi=None, 
        float32=False, **kwargs):
        """
        Combine subsets (e.g., a box or sphere) of data in different chunks 
        into one subset.

        Args:
            func (str): Types of subset, must be "box" or "sphere". This 
                argument determines the slicing method.
            partType (str or list of str): Particle types to be loaded.
            fields (str or list of str): Particle fields to be loaded.
            mdi (None or list of int, default to None): sub-indeces to be 
                loaded. None to load all.
            float32 (bool, default to False): Whether to use float32 or not.
            **kwargs: arguments to be sent to slicing function.

        Returns:
            dict: Subset of data.
        """

        # Make sure fields is not a single element
        if isinstance(fields, str):
            fields = [fields]

        # Make sure partType is not a single element
        if isinstance(partType, str):
            partType = [partType]


        if self._parallel:

            para_list = []
            for j, d in enumerate(self._datasets):
                para_list.append((d, kwargs["boundary"], partType, fields, mdi, float32))

            with Pool(self._Np) as pool:
                results = pool.starmap(_box_lazy, para_list)

        else:
            results = []
            for j, d in enumerate(self._datasets):
                if func == "box":
                    r = d.box(kwargs["boundary"], 
                        partType, fields, mdi, float32)
                if func == "box_lazy":
                    r = d.box_lazy(kwargs["boundary"], 
                        partType, fields, mdi, float32)
                elif func == "sphere":
                    r = d.sphere(kwargs["center"], kwargs["radius"], 
                        partType, fields, mdi, float32)
                else:
                    raise ValueError("func must be either \"box\" or \"sphere\"!")

                results.append(r)

        for j, r in enumerate(results):
            if j == 0:
                result = r
            else:
                # Loop over particle types
                for p in partType:
                    # Loop over each requested field for this particle type
                    for i, field in enumerate(fields):
                        # read data local to the current file
                        if mdi is None or mdi[i] is None:
                            result[p][field] = _concatenate_enable_empty(
                                result[p][field], r[p][field][:])
                        else:
                            result[p][field] = _concatenate_enable_empty(
                                result[p][field], r[p][field][:,mdi[i]])

        return result
    
    def box(self, boundary, partType, fields, mdi=None, float32=False, lazy=False):
        """
        Load a sub-box of data.

        Args:
            boundary (numpy.ndarray of scalar): Boundary of the box, with 
                shape of (3, 2).
            partType (str or list of str): Particle types to be loaded.
            fields (str or list of str): Particle fields to be loaded.
            mdi (None or list of int, default to None): sub-indeces to be 
                loaded. None to load all.
            float32 (bool, default to False): Whether to use float32 or not.
            lazy (bool, default to False): Lazy mode (no indexing)

        Returns:
            dict: Sub-box of data.
        """
        if lazy:
            return self._combine("box_lazy", partType, fields, mdi, float32, 
                boundary=boundary)
        return self._combine("box", partType, fields, mdi, float32, 
            boundary=boundary)

    def sphere(self, center, radius, partType, fields, mdi=None, 
        float32=False):
        """
        Load a sub-sphere of data.

        Args:
            center (numpy.ndarray of scalar): Center of the sphere, with 
                shape of (3,).
            radius (scalar): Radius of the sphere.
            partType (str or list of str): Particle types to be loaded.
            fields (str or list of str): Particle fields to be loaded.
            mdi (None or list of int, default to None): sub-indeces to be 
                loaded. None to load all.
            float32 (bool, default to False): Whether to use float32 or not.

        Returns:
            dict: Sub-sphere of data.
        """
        return self._combine("sphere", partType, fields, mdi, float32, 
            center=center, radius=radius)
        
class SingleDataset(object):
    """SingleDataset class stores a chunck of snapshot."""

    def __init__(self, fn, partType, depth=8, index_path=None):
        """
        Args:
            fn (str): File name to be loaded.
            partType (str or list of str): Particle types to be loaded.
            depth (int, default to 8): Depth of Mesh. For example, depth = 8
                corresponds to the Mesh dimension of (2^8, 2^8, 2^8).
            index_path (str): Path to store the index files. None to store 
                with the data.
        """

        super(SingleDataset, self).__init__()

        self._fn = fn

        # Make sure partType is not a single element
        if isinstance(partType, str):
            partType = [partType]
        self._partType = partType

        self._depth = depth

        self._index_path = index_path
        suffix = ".idx_d%02d.h5"%depth
        if index_path:
            self._index_fn = index_path + fn[fn.rfind("/"):] + suffix
        else:
            self._index_fn = fn + suffix

        self._index = None
        with h5py.File(fn, 'r') as f:
            self._box_size = f['Header'].attrs['BoxSize']
            self._boundary = np.array([[0., 0., 0.],
                [self._box_size, self._box_size, self._box_size]])

        # Set the int type for Mesh
        if depth <= 10:
            # By setting dtype to int32, the maximum level is 10
            self._int_tree = np.int32
        elif depth <= 20:
            # By setting dtype to int64, the maximum level is 20
            self._int_tree = np.int64
        else:
            raise ValueError("The depth of Mesh must be no more than 20!")

    @property
    def fn(self):
        """str: File name to be loaded."""
        return self._fn

    @property
    def partType(self):
        """str or list of str: Particle types to be loaded."""
        return self._partType

    @property
    def box_size(self):
        """scalar: Box size of the simulation."""
        return self._box_size

    @property
    def index(self):
        """dict: Newly generated or cached index of the Dataset. """

        if self._index:
            return self._index

        # Generate index
        self._index = {}

        # Find index file, otherwise create
        with h5py.File(self._index_fn,'a') as f:
            for p in self._partType:
                ptNum = partTypeNum(p)
                gName = "PartType%d"%(ptNum)
                self._index[gName] = {}

                # Load index if exists in index file 
                if "/"+gName in f.keys():
                    self._index[gName]["count"] = f[gName].attrs["count"]

                    self._index[gName]["index"] = f[gName]["index"][:]
                    self._index[gName]["mark"] = f[gName]["mark"][:]
                    
                # Compute and save index if does not exist in index file
                else:
                    data = loadFile(self._fn, self._partType, "Coordinates")
                    grp = f.create_group(gName)

                    length = data[p]["count"]
                    self._index[gName]["count"] = length
                    grp.attrs["count"] =  length

                    pos = data[p]["Coordinates"] if length else np.array([])
                    
                    m = Mesh(pos, length, 0, self._boundary, self._depth)

                    (self._index[gName]["index"], 
                        self._index[gName]["mark"]) = m.build()
                    grp.create_dataset("index", 
                        data=self._index[gName]["index"], dtype=np.int64)
                    grp.create_dataset("mark", 
                        data=self._index[gName]["mark"], dtype=np.int64)

        return self._index

    def box(self, boundary, partType, fields, mdi=None, float32=True, 
        method="outer"):
        """
        Slicing method to load a sub-box of data.

        Note: The current version only support loading the outer or inner 
            box of the sub-box. Loading the exact sub-box is not supported.

        Args:
            boundary (numpy.ndarray of scalar): Boundary of the box, with 
                shape of (3, 2).
            partType (str or list of str): Particle types to be loaded.
            fields (str or list of str): Particle fields to be loaded.
            mdi (None or list of int, default to None): sub-indeces to be 
                loaded. None to load all.
            float32 (bool, default to False): Whether to use float32 or not.
            method (str, default to "outer"): How to load the box, must be 
                "outer" or "exact" or "inner".

        Returns:
            dict: Sub-box of data.
        """

        # Make sure fields is not a single element
        if isinstance(fields, str):
            fields = [fields]

        # Make sure partType is not a single element
        if isinstance(partType, str):
            partType = [partType]

        self.index # pre-indexing

        boundary_normalized = (
            2**self._depth * (boundary - self._boundary[0]) / 
            (self._boundary[1] - self._boundary[0]))

        if method in ["outer", "exact"]:
            lower = np.floor(boundary_normalized[0]).astype(self._int_tree)
            upper = np.ceil(boundary_normalized[1]).astype(self._int_tree)

        if method == "inner":
            lower = np.ceil(boundary_normalized[0]).astype(self._int_tree)
            upper = np.floor(boundary_normalized[1]).astype(self._int_tree)

        targets = []
        tt0 = 0
        # Use for loop here assuming the box is small
        for p in partType:
            ptNum = partTypeNum(p)
            gName = "PartType%d"%(ptNum)

            t0 = time.time()
            target = _slicing(lower, upper, self._index[gName]["mark"], 
                self._index[gName]["index"], self._depth, self._int_tree)
            tt0 += time.time() - t0

            targets.append(target)

        print("time: %.3fs"%tt0)
        return loadFile(self._fn, partType, fields, mdi, float32, targets)


    def box_lazy(self, boundary, partType, fields, mdi=None, float32=True, 
        method="outer"):
        """
        Slicing method to load a sub-box of data in lazy mode.

        Note: The current version only support loading the outer or inner 
            box of the sub-box. Loading the exact sub-box is not supported.

        Args:
            boundary (numpy.ndarray of scalar): Boundary of the box, with 
                shape of (3, 2).
            partType (str or list of str): Particle types to be loaded.
            fields (str or list of str): Particle fields to be loaded.
            mdi (None or list of int, default to None): sub-indeces to be 
                loaded. None to load all.
            float32 (bool, default to False): Whether to use float32 or not.
            method (str, default to "outer"): How to load the box, must be 
                "outer" or "exact" or "inner".

        Returns:
            dict: Sub-box of data.
        """

        # Make sure fields is not a single element
        if isinstance(fields, str):
            fields = [fields]

        # Make sure partType is not a single element
        if isinstance(partType, str):
            partType = [partType]

        targets = []
        tt0 = 0

        # Use for loop here assuming the box is small
        for p in partType:
            data = loadFile(self._fn, p, "Coordinates")
            pos = data[p]["Coordinates"]
            x = pos[:,0]
            y = pos[:,1]
            z = pos[:,2]
            target = np.where(
                (x>boundary[0,0])&(x<boundary[1,0])&
                (y>boundary[0,1])&(y<boundary[1,1])&
                (z>boundary[0,2])&(z<boundary[1,2]))
            targets.append(target)

        print("time: %.3fs"%(time.time()-tt0))
        return loadFile(self._fn, partType, fields, mdi, float32, targets)


    def sphere(self, center, radius, partType, fields, mdi=None, 
        method="outer"):
        """
        Slicing method to load a sub-sphere of data.

        Note: This function is not supported in the current version

        Args:
            center (numpy.ndarray of scalar): Center of the sphere, with 
                shape of (3,).
            radius (scalar): Radius of the sphere.
            partType (str or list of str): Particle types to be loaded.
            fields (str or list of str): Particle fields to be loaded.
            mdi (None or list of int, default to None): sub-indeces to be 
                loaded. None to load all.
            float32 (bool, default to False): Whether to use float32 or not.
            method (str, default to "outer"): How to load the box, must be 
                "outer" or "exact" or "inner".
        """
        pass


def _concatenate_enable_empty(arr1, arr2):
    """
    Concatenate two arrays allowing one or two to be empty.
    """
    s1 = arr1.shape
    s2 = arr2.shape
    if len(s1) == 1 and len(s2) == 2:
        return np.concatenate((arr1.reshape(0, s2[1]), arr2))
    if len(s1) == 2 and len(s2) == 1:
        return np.concatenate((arr1, arr2.reshape(0, s1[1])))
    return np.concatenate((arr1, arr2))


# Speeding up slicing with numba.jit
from numba import jit, typed, types

@jit(nopython=True)
def _slicing(lower, upper, mark, index, depth, int_tree):
    """
    Slice the index file according to lower/upper boundaries.
    """
    target = typed.List.empty_list(types.int64)
    shifter = np.array([4**depth,2**depth,1], dtype=int_tree)
    for i in range(lower[0], upper[0]):
        for j in range(lower[1], upper[1]):
            idx_3d_lower = np.array([i, j, lower[2]], dtype=int_tree)
            idx_1d_lower = np.sum(idx_3d_lower * shifter)
            idx_3d_upper = np.array([i, j, upper[2]], dtype=int_tree)
            idx_1d_upper = np.sum(idx_3d_upper * shifter)

            start = mark[idx_1d_lower]
            end = mark[idx_1d_upper]
            target.extend(index[start:end])

    return target


def _box_lazy(d, boundary, partType, fields, mdi=None, float32=True, 
    method="outer"):
    """
    Slicing method to load a sub-box of data in lazy mode.

    Note: The current version only support loading the outer or inner 
        box of the sub-box. Loading the exact sub-box is not supported.

    Args:
        d (SingleDataset)
        boundary (numpy.ndarray of scalar): Boundary of the box, with 
            shape of (3, 2).
        partType (str or list of str): Particle types to be loaded.
        fields (str or list of str): Particle fields to be loaded.
        mdi (None or list of int, default to None): sub-indeces to be 
            loaded. None to load all.
        float32 (bool, default to False): Whether to use float32 or not.
        method (str, default to "outer"): How to load the box, must be 
            "outer" or "exact" or "inner".

    Returns:
        dict: Sub-box of data.
    """

    # Make sure fields is not a single element
    if isinstance(fields, str):
        fields = [fields]

    # Make sure partType is not a single element
    if isinstance(partType, str):
        partType = [partType]

    targets = []
    tt0 = 0

    # Use for loop here assuming the box is small
    for p in partType:
        data = loadFile(d._fn, p, "Coordinates")
        pos = data[p]["Coordinates"]
        x = pos[:,0]
        y = pos[:,1]
        z = pos[:,2]
        target = np.where(
            (x>boundary[0,0])&(x<boundary[1,0])&
            (y>boundary[0,1])&(y<boundary[1,1])&
            (z>boundary[0,2])&(z<boundary[1,2]))
        targets.append(target)

    print("time: %.3fs"%(time.time()-tt0))
    return loadFile(d._fn, partType, fields, mdi, float32, targets)