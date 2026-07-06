__all__ = ['CR3']


from CR3.Utils import mb

from CR3.FTYP import *
from CR3.MOOV import *
from CR3.XPacket import *
from CR3.Preview import *
from CR3.MDAT import *

from pathlib import Path


class CR3:
	def __init__(
		self, 
		data: bytearray
	) -> None:
		"""
			Parses a CR3 file into a python Objects.

			Parameters:
			-----------
				data <bytearray>

			Attributes:
			-----------
				data <bytearray>
				ftyp <CR3.FTYP>
				moov <CR3.MOOV>
				xpacket <CR3.XPacket>
				preview <CR3.Preview>
				mdat <CR3.MDAT>
		"""

		self.data: bytearray = data

		offset = 0 
		self.ftyp = FTYP(data)
		offset = self.ftyp.size
		self.moov = MOOV(data[offset:])
		offset += self.moov.size
		self.xpacket = XPacket(data[offset:])
		offset+= self.xpacket.size
		self.preview = Preview(data[offset:])
		offset += self.preview.size
		self.mdat = MDAT(data[offset:])


	@property
	def size(self) -> int:
		"""
			Returns the size of the image file in Mega Bytes (mb).
			
			[!Note]: Returns 0 if the file size is less than 1 mb!
		"""
		
		if len(self.data) < 1048576: # Minimum MB value
			return 0

		return round(mb(len(self.data)))


	def _parse(self) -> None:
		from time import time

		clock: float = time()

		data: dict[str, list] = {}

		tags: list[str] = [
			"ftyp",
			"moov",
			"uuid",
			"mdat",
			"free",
			"mvhd",
			"trak",
			"tkhd",
			"mdia",
			"hdlr",
			"minf",
			"dinf",
			"stbl",
			"dref",
			"stsd",
			"stts",
			"stsc",
			"stsz",
			"co64",
			"nmhd",
		]

		offset: int = 0
		for i in range(len(self.data)):
			a: int = 3
			b = self.data[offset:i + a]

			try:
				tag: str = b.decode("utf-8")
			except:
				try:
					int.from_bytes(b)
				except:
					print(b)

			if tag in tags:
				size: int = int.from_bytes(
					self.data[offset - 4:i - 1]
				)

				print(tag, size, offset)

				data[f"{tag}::{size}"] = str(self.data[i + a:size][:12]) # content

			offset = i

		from json import dumps

		with open("CR3_parsed.json", '+w') as file:
			file.write(
				dumps(data)
			)

			print(f"Parsed in {round(time() - clock)}s")
			print(Path.cwd(), "/CR3_parsed.json", sep="")


	def parse(self, text_file: bool = False) -> None:
		"""
			Parses the file binary into readable text.

			Parameters:
			-----------
				[optional] text_file <bool> = False
				-|	Outputs the text into a txt file when True.
		"""

		fields: tuple = (
			self.ftyp,
			self.moov,
			self.xpacket,
			self.preview,
			self.mdat
		)

		if not text_file:
			print(*fields, sep="\n")

			return

		text: str = ""
		for field in fields:
			text += str(field) + "\n"

		with open("CR3_dump.txt", '+w') as file:
			file.write(text)

		print(Path.cwd(), "/CR3_dump.bin", sep="")

		

