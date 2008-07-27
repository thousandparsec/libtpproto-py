
from xstruct import pack
from objects import Object

class Wormhole(Object):
	"""\
	The Wormhole is a top level object that links to locations together.

	It was added as a quick hack to make the Risk ruleset a little easier to play.

	It has 3 int64 arguments which are the "other end" of the wormhole.
	"""
	subtype = 5
	substruct = "qqq"

	def __init__(self, sequence, \
			id, type, name, \
			size, \
			startx, starty, startz, \
			velx, vely, velz, \
			contains, \
			order_types, \
			order_number, \
			modify_time, \
			endx, endy, endz):
		Object.__init__(self, sequence, \
			id, type, name, \
			size, \
			startx, starty, startz, \
			velx, vely, velz, \
			contains, \
			order_types, \
			order_number, \
			modify_time)

		self.length += 8*3
		self.start = self.pos
		self.end   = (endx, endy, endz)
	
	def __str__(self):
		output = Object.__str__(self)
		output += pack(self.substruct, *self.end)

		return output
