# Copyright (c) 2021 Bill Chen
# License: MIT (https://opensource.org/licenses/MIT)

import numpy

class octree(object):
	"""docstring for octree"""

	def __init__(self, pos, length, offset, boundary, depth):
		super(octree, self).__init__()

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

		# Set the int type for octree
		if depth <= 10:
			# By setting dtype to int32, the maximum level is 10
			self._int_tree = np.int32
		elif depth <=20:
			# By setting dtype to int64, the maximum level is 20
			self._int_tree = np.int64
		else:
			raise ValueError("The depth of octree must be no more than 20!")


	@property
	def boundary(self):
		return self._boundary

	@property
	def depth(self):
		return self._depth

	def build(self):
		idx_3d = np.astype(
			2**self._level * (self._pos - self._boundary[0]) / 
			(self._boundary[1] - self._boundary[0]), dtype=self._int_tree)

		# Conbine 3D index into 1D 
		idx_1d = np.sum(np.left_shift(idx_3d, [2*self._depth,self._depth,0]))

		# Sort rank with index
		idx = np.argsort(idx_1d)

		idx_all = np.arange(8**self._level, dtype=self._int_tree)
		mark = np.np.empty_like(idx_all+1, dtype=self._int_data)
		mark[0] = 0
		mark[1:] = np.searchsorted(idx_1d, idx_all, side="right", sorter=idx)

		rank = np.arange(self._offset, self._offset+self._length, 
			dtype=self._int_data)
		rank = rank[idx]
		return rank, mark


	
	