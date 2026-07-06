__all__ = ['blen', 'klen', 'mlen']


from .memory_units import kb, mb


def blen(data: bytearray) -> str:
	return f"({hex(l:=len(data))}::{l}bytes)"

def klen(data: bytearray) -> str:
	return f"({hex(l:=len(data))}::{kb(l)}kb)"

def mlen(data: bytearray) -> str:
	return f"({hex(l:=len(data))}::{mb(l)}mb)"