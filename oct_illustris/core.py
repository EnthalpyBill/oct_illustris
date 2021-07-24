# Copyright (c) 2021 Bill Chen
# License: MIT (https://opensource.org/licenses/MIT)

import os
import numpy as np
import h5py

from .il_util import *
from .octree import octree

__all__ = ["dataset", "singleDataset"]

class dataset(object):
    """docstring for dataset"""
    def __init__(self, datasets, n_chunk):
        super(dataset, self).__init__()
        self._datasets = datasets
        self._n_chunk = n_chunk

    @property
    def datasets(self):
        return self._datasets

    @property
    def n_chunk(self):
        return self._n_chunk

    def _combine(self, func, partType, fields, mdi=None, float32=False, **kwargs):
        for j, d in enumerate(self._datasets):
            if func == "box":
                r = d.box(kwargs["boundary"], 
                    partType, fields, mdi, float32)
            elif func == "sphere":
                r = d.sphere(kwargs["center"], kwargs["radius"], 
                    partType, fields, mdi, float32)

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
        return self._combine("box", partType, fields, mdi, float32, 
            boundary=boundary)

    def sphere(self, center, radius, partType, fields, mdi=None, float32=False):
        return self._combine("sphere", partType, fields, mdi, float32, 
            center=center, radius=radius)

    
        
class singleDataset(object):
    """docstring for dataset"""
    def __init__(self, fn, partType, depth=8, index_path=None):
        super(singleDataset, self).__init__()

        self._fn = fn

        # Make sure partType is not a single element
        if isinstance(partType, str):
            partType = [partType]
        self._partType = partType

        self._depth = depth

        self._pt_idx = 0

        for p in partType:
            self._pt_idx += 2**partTypeNum(p)

        self._index_path = index_path
        suffix = ".idx_d%02d_pt%02d.h5"%(depth, self._pt_idx)
        if index_path:
            self._index_fn = index_path + fn[fn.rfind("/"):] + suffix
        else:
            self._index_fn = fn + suffix

        self._index = None
        with h5py.File(fn, 'r') as f:
            self._box_size = f['Header'].attrs['BoxSize']
            self._redshift = f['Header'].attrs['Redshift']
            self._boundary = np.array([[0., 0., 0.],
                [self._box_size, self._box_size, self._box_size]])

        # Set the int type for octree
        if depth <= 10:
            # By setting dtype to int32, the maximum level is 10
            self._int_tree = np.int32
        elif depth <=20:
            # By setting dtype to int64, the maximum level is 20
            self._int_tree = np.int64
        else:
            raise ValueError("The depth of octree must be no more than 20!")

        # Set the int type for data
        self._int_data = np.int64

    @property
    def fn(self):
        return self._fn

    @property
    def partType(self):
        return self._partType

    @property
    def box_size(self):
        return self._box_size

    @property
    def redshift(self):
        return self._redshift

    @property
    def index(self):
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
                ot = octree(pos, length, 0, self._boundary, self._depth)

                self._index[gName]["index"], self._index[gName]["mark"] = ot.build()
                grp.create_dataset("index", 
                    data=self._index[gName]["index"], dtype=self._int_data)
                grp.create_dataset("mark", 
                    data=self._index[gName]["mark"], dtype=self._int_data)

        return self._index

    def box(self, boundary, partType, fields, mdi=None, float32=True, 
        method="outer"):
    
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
                    for k in range(lower[2], upper[2]):
                        idx_3d = [i, j, k]
                        idx_1d = np.sum(np.left_shift(
                            idx_3d, [2*self._depth,self._depth,0]))

                        start = self._index[gName]["mark"][idx_1d]
                        end = self._index[gName]["mark"][idx_1d+1]
                        target = (np.r_[target, 
                            self._index[gName]["index"][start:end]])

            targets.append(target)

        return loadFile(fn, partType, fields, mdi, float32, targets)


    def sphere(self, center, radius, partType, fields, mdi=None, method="outer"):
        pass