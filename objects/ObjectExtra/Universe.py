
from xstruct import pack
from objects import Object

class Universe(Object):
	"""\
	The Universe is the top level object, everyone can always get it. It does not handle much itself.

	It only has one piece of data, that is the int32 turn number, also know as the year since game start.
	"""
	subtype = 0
	substruct = "I"

	def __init__(self, sequence, \
			id, type, name, \
			size, \
			posx, posy, posz, \
			velx, vely, velz, \
			contains, \
			order_types, \
			order_number, \
			modify_time, \
			turn):
		Object.__init__(self, sequence, \
			id, type, name, \
			size, \
			posx, posy, posz, \
			velx, vely, velz, \
			contains, \
			order_types, \
			order_number, \
			modify_time)

		self.length += 4
		self.turn = turn
	
	def __repr__(self):
		output = Object.__repr__(self)
		output += pack(self.substruct, self.turn)

		return output
