
from xstruct import pack
from objects import *

class Move(Order):
	"""\
	Move to a place in space.
	"""
	subtype = 1
	substruct = "qqq"

	name = "Move"

	# Arguments
	names = [("pos", constants.ARG_ABS_COORD)]

	# Argument descriptions
	pos__doc__ = "Position to move to."
	
	def __init__(self, sequence, \
					id,	slot, type, turns, resources, \
					x, y=None, z=None):
		Order.__init__(self, sequence, \
					id, slot, type, turns, resources)

		self.length += 3*8

		if z==None or y==None:
			self.pos = x
		else:
			self.pos = (x, y, z)

	def __str__(self):
		output = Order.__str__(self)
		output += pack(self.substruct, self.pos[0], self.pos[1], self.pos[2])

		return output
