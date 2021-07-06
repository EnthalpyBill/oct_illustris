import os
import numpy as np
import h5py

from .il_util import partTypeNum
from .loader import loadFile
from .octree import octree

class dataset(object):
    """docstring for dataset"""
    def __init__(self, fn, pt, height=8, index_fn=None):
        super(dataset, self).__init__()

        self._fn = fn
        self._pt = pt
        self._height = height

        self._pt_idx = 0

        for p in pt:
            self._pt_idx += 2**partTypeNum(p)

        if index_fn:
            self._index_fn = index_fn
        else:
            self._index_fn = fn + ".idx_h%02d_pt%02d.h5"%(height, self._pt_idx)

        self._index = None
        with h5py.File(fn, 'r') as f:
            self._box_size = f['Header'].attrs['BoxSize']
            self._redshift = f['Header'].attrs['Redshift']
            self._boundary = np.array([[0., 0., 0.],
                [self._box_size, self._box_size, self._box_size]])

    @property
    def fn(self):
        return self._fn

    @property
    def pt(self):
        return self._pt

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
                for p in self._pt:
                    ptNum = partTypeNum(p)
                    gName = "PartType%d"%(ptNum)
                    self._index[gName]["count"] = f[gName].attrs["count"]

                    if not self._index[gName]["count"]:
                        continue

                    self._index[gName]["index"] = f[gName]["index"][:]

            return self._index

        # Compute and save index if index file does not exist
        data = loadFile(fn, self._pt, "Coordinates")
        with h5py.File(self._index_fn,'w') as f:
            # Loop over each requested field for this particle type
            for p in self._pt:
                ptNum = partTypeNum(p)
                gName = "PartType%d"%(ptNum)
                grp = f.create_group(gName)

                length = data[gName]["count"]
                result[gName]["count"] = length
                grp.attrs["count"] =  length

                if not length:
                    continue

                pos = data[gName]["Coordinates"]
                ot = octree(pos, length, 0, self._boundary, self._height)

                self._index[gName]["index"] = ot.build()
                grp.create_dataset("index", 
                    data=self._index[gName]["index"], dtype="u4")

        return self._index

