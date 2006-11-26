
from xstruct import pack
from objects import Object

class Galaxy(Object):
	"""\
	The Galaxy is a container for a large group of close star systems, like the Milky Way.
	
	The Galaxy contains no extra data.
	"""
	subtype = 1
	substruct = ""

	def __init__(self, sequence, \
			id, type, name, \
			size, \
			posx, posy, posz, \
			velx, vely, velz, \
			contains, \
			order_types, \
			order_number, \
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
			
		self.length += 0
