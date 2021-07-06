import os
import numpy as np

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

        if index_fn:
            self._index_fn = index_fn
        else:
            self._index_fn = fn + ".idx_h%02d.h5"%(height)

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
            return 1

        if os.path.isfile(self._index_fn):
            # Load index
            return 1

        # Generate index
        data = loadFile(fn, self._pt, "Coordinates")

        # Loop over each requested field for this particle type
        for i, field in enumerate(fields):
            ptNum = partTypeNum(pt)
            gName = "PartType%01d"%(ptNum)
            length = data[gName]["count"]
            if not length:
                continue

            pos = data[gName]["Coordinates"]
            ot = octree(pos, length, 0, self._boundary, self._height)
            idx = ot.build()

