# -*- coding: utf-8 -*-
# Copyright (c) 2021 Bill Chen
# License: MIT (see LICENSE)
# 
# Part of this file is based on the illustris_python project:
# Copyright (c) 2017, illustris & illustris_python developers
# License: FreeBSD (see LICENSE_bundled)

"""
loader module defines a convenient load() function to load snapshots in 
Illustris or IllustrisTNG
"""

import numpy as np
import h5py

from .core import Dataset, SingleDataset
from .il_util import partTypeNum, snapPath, getNumPart

__all__ = ["load"]

def load(basePath, snapNum, partType, depth=8, index_path=None):
    """
    Function to load snapshots in Illustris or IllustrisTNG.

    Args:
        basePath (str): Base path of the simulation data. This path usually 
            ends with "output".
        snapNum (int): Number of the snapshot.
        partType (str or list of str): Particle types to be loaded.
        depth (int, default to 8): Depth of mesh. For example, depth = 8
            corresponds to the mesh dimension of (2^8, 2^8, 2^8).
        index_path (str): Path to store the index files. None to store 
            with the data.

    Returns:
        `Dataset`: Structured data.
    """

    # Determine number of chunks
    with h5py.File(snapPath(basePath, snapNum), "r") as f:
        n_chunk = f["Header"].attrs["NumFilesPerSnapshot"]

    d = []
    # Loop over chunks
    for i in range(n_chunk):
        fn = snapPath(basePath, snapNum, i)
        d.append(SingleDataset(fn, partType, depth, index_path))

    return Dataset(d, n_chunk)