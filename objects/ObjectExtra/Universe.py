
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
			turn):
		Object.__init__(self, sequence, \
			id, type, name, \
			size, \
			posx, posy, posz, \
			velx, vely, velz, \
			contains, \
			order_types, \
			order_number)

		self.turn = turn
