# -*- coding: utf-8 -*-
# Copyright (c) 2021 Bill Chen
# License: MIT (see LICENSE)

"""
mesh module defines the Mesh to tessellate the entire volume.
"""

import numpy as np

__all__ = ["Mesh"]

class Mesh(object):
    """Mesh class tessellates the entire volume."""

    def __init__(self, pos, length, offset, boundary, depth):
        """
        Args:
            pos (numpy.ndarray of scalar): Positions of points, with shape of 
                (length, 3).
            length (int): Number of points to be tessellated.
            offset (int): Starting index of points. Often used when there are
                too many points, which need to be separated to many groups.
            boundary (numpy.ndarray of scalar): Boundary of the box, with 
                shape of (3, 2).
            depth (int, default to 8): Depth of Mesh. For example, depth = 8
                corresponds to the Mesh dimension of (2^8, 2^8, 2^8).
        """

        super(Mesh, self).__init__()

        self._pos = pos
        self._length = length
        self._offset = offset
        self._boundary = boundary
        self._depth = depth

        # Set the int type for data
        if length <= 2147483647:
            self._int_data = np.int32
        else:
            self._int_data = np.int64

        # Set the int type for Mesh
        if depth <= 10:
            # By setting dtype to int32, the maximum level is 10
            self._int_tree = np.int32
        elif depth <=20:
            # By setting dtype to int64, the maximum level is 20
            self._int_tree = np.int64
        else:
            raise ValueError("The depth of Mesh must be no more than 20!")


    @property
    def boundary(self):
        """numpy.ndarray of scalar: Boundary of the box, with 
            shape of (3, 2)."""
        return self._boundary

    @property
    def depth(self):
        """int, default to 8: Depth of Mesh. For example, depth = 8
                corresponds to the Mesh dimension of (2^8, 2^8, 2^8)"""
        return self._depth

    def build(self):
        """
        Build index for the points according to the Mesh.
        The indexing process produces a "rand" and a "mark" variables, which 
        link the index of each point to its location in the Mesh.

        Returns:
            tuple of numpy.ndarray of int: (rank, mark).
        """

        idx_3d = (2**self._depth * (self._pos - self._boundary[0]) //
            (self._boundary[1] - self._boundary[0])).astype(self._int_tree)

        # Conbine 3D index into 1D 
        idx_1d = np.sum(
            np.left_shift(idx_3d, [2*self._depth,self._depth,0]), axis=1)

        # Sort rank with index
        idx = np.argsort(idx_1d)
        idx_all = np.arange(8**self._depth, dtype=self._int_tree)

        mark = np.zeros(8**self._depth+1, dtype=self._int_data)
        mark[1:] = np.searchsorted(idx_1d, idx_all, side="right", sorter=idx)

        rank = np.arange(self._offset, self._offset+self._length, 
            dtype=self._int_data)
        rank = rank[idx]

        return rank, mark


    
    