__all__ = ['FTYP']


from .ABC import ABC

from CR3.Utils import blen


class FTYP(ABC):
	def __init__(self, data: bytearray) -> None:
		"""
			File type box.

			Attributes:
			-----------
				tag <str>\n
				major_brand <str>\n
				minor_version <int>\n
				other <list[bytearray]>
		"""
		super().__init__(data)

		self.tag: str = data[4:8].decode("utf-8")
		self.major_brand: str = data[8:12].decode("utf-8")
		self.minor_version: int = int.from_bytes(data[12:16])
		self.other: list[bytearray] = [
			data[16:20],
			data[20:24]
		]


	def __str__(self) -> str:
		return " ".join([
			f"{self.tag}:",
			f"major_brand={self.major_brand},",
			f"minor_version={self.minor_version},",
			str(self.other),
			blen(self.data)
		])