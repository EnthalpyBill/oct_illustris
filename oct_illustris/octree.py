import numpy

class octree(object):
	"""docstring for octree"""

	def __init__(self, pos, length, offset, boundary, height):
		super(octree, self).__init__()

		self._pos = pos
		self._length = length
		self._offset = offset
		self._boundary = boundary
		self._height = height

	@property
	def boundary(self):
		return self._boundary

	@property
	def height(self):
		return self._height

	def build(self):
		# By setting dtype to int64, the maximum level is 20 (2^(3*20)<2^63-1)
		idx_3d = np.astype(
			2**self._level * (self._pos - self._boundary[0]) / 
			(self._boundary[1] - self._boundary[0]), dtype='i8')

		# Conbine 3D index into 1D 
		idx_1d = np.left_shift(idx_3d, [2*self._height,self._height,0])

		# Sort rank with index
		rank = np.arange(self._offset, self._offset+self._length, dtype='i8')
		return rank[np.argsort(idx_1d)]


	
	