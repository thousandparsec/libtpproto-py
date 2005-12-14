
from xstruct import pack
from objects import Object

class Fleet(Object):
	"""\
	A fleet is a collection of ships. Many different ships can make up a fleet.

	A fleet has an owner, Int32 Player ID.
	"""
	subtype = 4
	substruct = "I[II]I"

	def __init__(self, sequence, \
			id, type, name, \
			size, \
			posx, posy, posz, \
			velx, vely, velz, \
			contains, \
			order_types, \
			order_number, \
			modify_time, \
			owner, ships, damage):
		Object.__init__(self, sequence, \
			id, type, name, \
			size, \
			posx, posy, posz, \
			velx, vely, velz, \
			contains, \
			order_types, \
			order_number, \
			modify_time)

		self.length += 4 + 4 + len(ships) * 8 + 4

		self.owner = owner
		# FIXME: Hack
		if self.owner == 4294967295:
			self.owner = -1
		self.ships = ships
		self.damage = damage

	def __str__(self):
		output = Object.__str__(self)
		output += pack(self.substruct, self.owner, self.ships, self.damage)

		return output
