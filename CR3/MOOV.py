__all__ = ['MOOV']


from CR3.ABC import ABC


class MOOV(ABC):
	class UUID(ABC):
		def __init__(self, data: bytearray) -> None:
			"""
				Attributes:
				-----------
					uuid <str>
			"""
			super().__init__(data)

			self.uuid: str = self.data.hex()

	
	class MVHD(ABC):
		def __init__(self, data: bytearray) -> None:
			"""
				Attributes:
				-----------
					tag <str>\n
					mvhd <str>
			"""
			super().__init__(data)

			self.tag: str = self.data[4:8]
			self.mvhd: str = data[8:self.size].hex()


	class TRAK(ABC):
		def __init__(self, data: bytearray) -> None:
			"""
				Attributes:
				-----------
					...
			"""
			super().__init__(data)


	def __init__(self, data: bytearray) -> None:
		"""
			Container box whose sub-boxes define the metadata for a presentation.

			Attributes:
			-----------
				tag <str>
				uuid <MOOV.UUID>
				mvhd <MOOV.MVHD>
				trak1 <MOOV.TRAK>
				trak2 <MOOV.TRAK>
				trak3 <MOOV.TRAK>
				trak4 <MOOV.TRAK>
		"""
		super().__init__(data)
		
		self.tag: str = data[4:8]
		self.uuid = self.UUID(data[8:])
		self.mvhd = self.MVHD(data[self.uuid.size+8:])

		self.rest: bytearray = data[self.mvhd.size:self.size][:64]


	def __str__(self) -> str:
		return "\n".join([f"{k}=={v}" for k,v in self.__dict__.items()])