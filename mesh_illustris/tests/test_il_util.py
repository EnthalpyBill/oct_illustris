# Copyright (c) 2021 Bill Chen
# License: MIT (see LICENSE)

import h5py
import pytest

from mesh_illustris.il_util import *

@pytest.mark.skip(reason="Test function is not ready.")
def test_loadFile():
    pass

@pytest.mark.parametrize("partType, is_error, expected", [
    (0, False, 0),
    ("0", False, 0),
    ("PartType0", False, 0),
    ("stars", False, 4),
    ("Stars", False, 4),
    # Errors
    ("ether", True, "Unknown particle type name.")])
def test_partTypeNum(partType, is_error, expected):
    if is_error:
        with pytest.raises(ValueError, match=expected):
            partTypeNum(partType)
    else:
        assert partTypeNum(partType) == expected

@pytest.mark.parametrize("basePath, snapNum, chunkNum, expected", [
    ("/output", 0, 0, "/output/snapdir_000/snap_000.0.hdf5"),
    ("/output", 135, 99, "/output/snapdir_135/snap_135.99.hdf5")])
def test_snapPath(basePath, snapNum, chunkNum, expected):
    assert snapPath(basePath, snapNum, chunkNum) == expected

@pytest.mark.skip(reason="Test function is not ready.")
def test_getNumPart():
    pass