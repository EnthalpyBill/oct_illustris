# Copyright (c) 2021 Bill Chen
# License: MIT (https://opensource.org/licenses/MIT)


# Part of this file is based on the illustris_python project:
# Copyright (c) 2017, illustris & illustris_python developers
# License: FreeBSD (https://opensource.org/licenses/BSD-2-Clause)

import numpy as np
import h5py

from .core import dataset, singleDataset
from .il_util import partTypeNum, snapPath, getNumPart

__all__ = ["load"]

def load(basePath, snapNum, partType, depth=8, index_path=None):
    # Determine number of chunks
    with h5py.File(snapPath(basePath, snapNum), "r") as f:
        n_chunk = f["Header"].attrs["NumFilesPerSnapshot"]

    d = []
    # Loop over chunks
    for i in range(n_chunk):
        fn = snapPath(basePath, snapNum, i)
        d.append(singleDataset(fn, partType, depth, index_path))

    return dataset(d, n_chunk)