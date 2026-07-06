__all__ = ['MDAT']


from CR3.ABC import ABC


class MDAT(ABC):
	def __init__(self, data: bytearray) -> None:
		"""
			Main data.
		"""
		# super().__init__(data)
		self.data = data[4:]
		self.size = len(self.data)

	
	...