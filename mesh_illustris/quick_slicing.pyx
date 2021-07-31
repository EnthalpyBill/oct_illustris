# -*- coding: utf-8 -*-
# Copyright (c) 2021 Bill Chen
# License: MIT (see LICENSE)

import numpy as np

def slicing(lower, upper, mark, index, depth, int_tree):
    """
    Slice the index file according to lower/upper boundaries.
    """
    target = np.array([], dtype=np.int64)
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