__all__ = ['ABC']


class ABC:
	def __init__(self, data: bytearray) -> None:
		"""
			Parameters:
			-----------
				data <bytearray>

			Attributes:
			-----------
				size <int>\n
				data <bytearray>
		"""

		self.size: int = int.from_bytes(data[:4])
		self.data: bytearray = data[4:self.size]