# -*- coding: utf-8 -*-
# Copyright (c) 2021 Bill Chen
# License: MIT (see LICENSE)
# 
# Part of this file is based on the illustris_python project:
# Copyright (c) 2017, illustris & illustris_python developers
# License: FreeBSD (see LICENSE_bundled)

"""
il_util module defines some commonly used functions for Illustris.
"""

import numpy as np
import h5py

__all__ = ["loadFile", "partTypeNum", "snapPath", "getNumPart"]

def loadFile(fn, partType, fields=None, mdi=None, float32=True, index=None):
    """
    Load a subset of particles/cells in one chunk file. 
    This function applies numpy.memmap to minimize memory usage.

    Args:
        fn (str): File name to be loaded.
        partType (str or list of str): Particle types to be loaded.
        fields (str or list of str): Particle fields to be loaded.
        mdi (None or list of int, default to None): sub-indeces to be 
            loaded. None to load all.
        float32 (bool, default to False): Whether to use float32 or not.
        index (list of list of int): List of Fancy indices for slicing.

    Returns:
        dict: Entire or subset of data, depending on whether index == None.
    """

    # Make sure fields is not a single element
    if isinstance(fields, str):
        fields = [fields]

    # Make sure partType is not a single element
    if isinstance(partType, str):
        partType = [partType]
    
    result = {}
    with h5py.File(fn, "r") as f:
        for p in partType:
            ptNum = partTypeNum(p)
            gName = "PartType%d"%(ptNum)
            result[gName] = {}

            numType = f["Header"].attrs["NumPart_ThisFile"][ptNum]
            result[gName]["count"] = numType
            if not numType:
                continue

            # Loop over each requested field for this particle type
            for i, field in enumerate(fields):
                # Allocate within return dict
                dtype = f[gName][field].dtype
                shape = f[gName][field].shape
                if dtype == np.float64 and float32: dtype = np.float32
                result[gName][field] = np.zeros(shape, dtype=dtype)

                # read data local to the current file
                ds = f[gName][field]
                offset = ds.id.get_offset()
                dtype = ds.dtype
                shape = ds.shape
                to_load = np.memmap(fn, mode="r", shape=shape, offset=offset, 
                    dtype=dtype)
                if index:
                    if mdi is None or mdi[i] is None:
                        result[gName][field] = to_load[index[i]]
                    else:
                        result[gName][field] = to_load[index[i],mdi[i]]
                else:
                    if mdi is None or mdi[i] is None:
                        result[gName][field] = to_load[:]
                    else:
                        result[gName][field] = to_load[:,mdi[i]]

    return result

def partTypeNum(partType):
    """
    Map common names to numeric particle types.

    Args:
        partType (str): Common names of particle type.

    Returns:
        int: Numeric particle type.
    """

    if str(partType)[-1].isdigit():
        return int(str(partType)[-1])
        
    if str(partType).lower() in ["gas","cells"]:
        return 0
    if str(partType).lower() in ["dm","darkmatter"]:
        return 1
    if str(partType).lower() in ["tracer","tracers","tracermc","trmc"]:
        return 3
    if str(partType).lower() in ["star","stars","stellar"]:
        return 4 # only those with GFM_StellarFormationTime>0
    if str(partType).lower() in ["wind"]:
        return 4 # only those with GFM_StellarFormationTime<0
    if str(partType).lower() in ["bh","bhs","blackhole","blackholes"]:
        return 5
    
    raise ValueError("Unknown particle type name.")

def snapPath(basePath, snapNum, chunkNum=0):
    """
    Return path to a chunk file of snapshot.

    Args:
        basePath (str): Base path of the simulation data. This path usually 
            ends with "output".
        snapNum (int): Number of the snapshot.
        chunkNum (int, default to 0): Number of the chunk.

    Returns:
        str: Path to a chunk file.
    """

    snapPath = basePath + "/snapdir_%03d/"%(snapNum)
    filePath = snapPath + "snap_%03d.%d.hdf5"%(snapNum, chunkNum)

    return filePath

def getNumPart(header):
    """
    Calculate number of particles of all types given a snapshot header.

    Args:
        header (h5py.Group): header of the snapshot.

    Returns:
        numpy.ndarray of int: Number of particles of each type.
    """

    nTypes = 6

    nPart = np.zeros(nTypes, dtype="i4")
    for j in range(nTypes):
        nPart[j] = (header["NumPart_Total"][j] | 
            (header["NumPart_Total_HighWord"][j] << 32))

    return nPart