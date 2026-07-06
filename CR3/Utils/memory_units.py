__all__ = [
	"kb", # Kilo Byte
	"mb", # Mega Byte
	"gb", # Giga Byte
	"tb", # Tera Byte
	"pb", # Peta Byte
	"hb", # Hexa Byte
	"zb", # Zetta Byte
	"yb", # Yotta Byte
]


from functools import partial


def _convert(value: int, divider: int) -> float:
	return round(value / divider)

for multiplier, name in enumerate(__all__):
	globals()[name] = partial(_convert, divider=1024 ** (multiplier + 1))