
from xstruct import pack
from objects import *

class NOp(Order):
	"""\
	A do no nothing order.
	"""
	subtype = 0
	substruct = "I"
	
	name = "Wait"
	names = [("wait", constants.ARG_TIME)]

	def __init__(self, sequence, \
					id,	type, slot, turns, resources, \
					wait):
		Order.__init__(self, sequence, \
					id, type, slot, turns, resources)

		self.length += 4
		self.wait = wait

	def __repr__(self):
		output = Order.__repr__(self)
		output += pack(self.substruct, self.wait)

		return output
