# -*- coding: utf-8 -*-
# Copyright (c) 2021 Bill Chen
# License: MIT (see LICENSE)

"""
core codes of the mesh_illustris package.
"""

import os
import numpy as np
import h5py

from .il_util import *
from .mesh import Mesh

__all__ = ["Dataset", "SingleDataset"]

class Dataset(object):
    """Dataset class stores a snapshot of simulation."""

    def __init__(self, datasets, n_chunk):
        """
        Args:
            datasets (list of SingleDataset): Chunks that store the 
                snapshot of simulation. 
            n_chunk (int): Number of chunks
        """

        super(Dataset, self).__init__()
        self._datasets = datasets
        self._n_chunk = n_chunk

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

        for j, d in enumerate(self._datasets):
            if func == "box":
                r = d.box(kwargs["boundary"], 
                    partType, fields, mdi, float32)
            elif func == "sphere":
                r = d.sphere(kwargs["center"], kwargs["radius"], 
                    partType, fields, mdi, float32)
            else:
                raise ValueError("func must be either \"box\" or \"sphere\"!")

            if j == 0:
                result = r
            else:
                # Loop over particle types
                for p in partType:
                    ptNum = partTypeNum(p)
                    gName = "PartType%d"%(ptNum)

                    # Loop over each requested field for this particle type
                    for i, field in enumerate(fields):
                        # read data local to the current file
                        if mdi is None or mdi[i] is None:
                            result[gName][field] = (np.r_[result[gName][field], 
                                r[gName][field][:]])
                        else:
                            result[gName][field] = (np.r_[result[gName][field], 
                                r[gName][field][:,mdi[i]]])

        return result
    
    def box(self, boundary, partType, fields, mdi=None, float32=False):
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

        Returns:
            dict: Sub-box of data.
        """
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

        pt_idx = 0
        for p in partType:
            pt_idx += 2**partTypeNum(p)

        self._index_path = index_path
        suffix = ".idx_d%02d_pt%02d.h5"%(depth, pt_idx)
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
        elif depth <=20:
            # By setting dtype to int64, the maximum level is 20
            self._int_tree = np.int64
        else:
            raise ValueError("The depth of Mesh must be no more than 20!")

        # Set the int type for data
        self._int_data = np.int64

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

        # Load index if index file exists
        if os.path.isfile(self._index_fn):
            with h5py.File(self._index_fn,'r') as f:
                for p in self._partType:
                    ptNum = partTypeNum(p)
                    gName = "PartType%d"%(ptNum)
                    self._index[gName] = {}
                    self._index[gName]["count"] = f[gName].attrs["count"]

                    if not self._index[gName]["count"]:
                        continue

                    self._index[gName]["index"] = f[gName]["index"][:]
                    self._index[gName]["mark"] = f[gName]["mark"][:]

            return self._index

        # Compute and save index if index file does not exist
        data = loadFile(self._fn, self._partType, "Coordinates")
        with h5py.File(self._index_fn, "w") as f:
            # Loop over particle types
            for p in self._partType:
                ptNum = partTypeNum(p)
                gName = "PartType%d"%(ptNum)
                self._index[gName] = {}
                grp = f.create_group(gName)

                length = data[gName]["count"]
                self._index[gName]["count"] = length
                grp.attrs["count"] =  length

                if not length:
                    continue
                elif length <= 2147483647:
                    self._int_data = np.int32
                else:
                    self._int_data = np.int64

                pos = data[gName]["Coordinates"]
                ot = Mesh(pos, length, 0, self._boundary, self._depth)

                self._index[gName]["index"], self._index[gName]["mark"] = ot.build()
                grp.create_dataset("index", 
                    data=self._index[gName]["index"], dtype=self._int_data)
                grp.create_dataset("mark", 
                    data=self._index[gName]["mark"], dtype=self._int_data)

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
        # Use for loop here assuming the box is small
        for p in partType:
            ptNum = partTypeNum(p)
            gName = "PartType%d"%(ptNum)

            target = np.array([], dtype=self._int_data)
            for i in range(lower[0], upper[0]):
                for j in range(lower[1], upper[1]):
                    idx_3d_lower = [i, j, lower[2]]
                    idx_1d_lower = np.sum(np.left_shift(
                        idx_3d_lower, [2*self._depth,self._depth,0]))
                    idx_3d_upper = [i, j, upper[2]]
                    idx_1d_upper = np.sum(np.left_shift(
                        idx_3d_upper, [2*self._depth,self._depth,0]))

                    start = self._index[gName]["mark"][idx_1d_lower]
                    end = self._index[gName]["mark"][idx_1d_upper]
                    target = (np.r_[target, 
                        self._index[gName]["index"][start:end]])

            targets.append(target)

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