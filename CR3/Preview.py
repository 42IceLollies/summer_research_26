__all__ = ['Preview']


from CR3.ABC import ABC

from CR3.Utils import klen


class Preview(ABC):
	class PRVW(ABC):
		def __init__(self, data: bytearray) -> None:
			"""
				JPEG image.

				Attributes:
				-----------
					width <int>\n
					height <int>\n
					jpeg_size <int>
			"""
			super().__init__(data)

			self.size: int = int.from_bytes(data[:4])
			self.data: bytearray = data[4:self.size]


		# def __str__(self) -> str:
		# 	...

	def __init__(self, data: bytearray) -> None:
		"""
			Preview data.

			Attributes:
				uuid <str>\n
				PRVW <Preview.PRVW>
		"""
		super().__init__(data)

		self.uuid: str = self.data.hex()
		self.prvw = self.PRVW(data[self.size:])


	def __str__(self) -> str:
		return " ".join([
			"uuid:",
			self.uuid[:32],
			klen(self.uuid),
			"\n\t",
			str(self.prvw),
			klen(self.data)
		])