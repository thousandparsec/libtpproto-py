
from xstruct import pack
from objects import Object

class Fleet(Object):
	"""\
	A fleet is a collection of ships. Many different ships can make up a fleet.

	A fleet has an owner, Int32 Player ID.
	"""
	subtype = 4
	substruct = "I"

	def __init__(self, sequence, \
			id, type, name, \
			size, \
			posx, posy, posz, \
			velx, vely, velz, \
			contains, \
			order_types, \
			order_number, \
			owner):
		Object.__init__(self, sequence, \
			id, type, name, \
			size, \
			posx, posy, posz, \
			velx, vely, velz, \
			contains, \
			order_types, \
			order_number)

		self.length += 4
		self.owner = owner

	def __repr__(self):
		output = Object.__repr__(self)
		output += pack(self.substruct, self.owner)

		return output