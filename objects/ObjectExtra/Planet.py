
from xstruct import pack
from objects import Object

class Planet(Object):
	"""\
	A planet is any body in space which is very large and naturally occuring.

	Planet objects have Int32 Player id, which is the owner of the planet.
	"""
	subtype = 3
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