
from xstruct import pack
from objects import Object

class StarSystem(Object):
	"""\
	A Star System contains one or more stars and any related objects. The star itself is not yet modeled.

	Star System objects do not have any extra data.
	"""
	subtype = 2
	substruct = ""

	def __init__(self, sequence, \
			id, type, name, \
			size, \
			posx, posy, posz, \
			velx, vely, velz, \
			contains, \
			order_types, \
			order_number,
			modify_time):
		Object.__init__(self, sequence, \
			id, type, name, \
			size, \
			posx, posy, posz, \
			velx, vely, velz, \
			contains, \
			order_types, \
			order_number, \
			modify_time)
