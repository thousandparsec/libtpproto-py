
from xstruct import pack
from objects import *

class NOp(Order):
	"""\
	A do no nothing order.
	"""
	subtype = 0
	substruct = "I"
	
	name = "NOp"

	# Arguments
	names = [("wait", constants.ARG_TIME)]

	# Argument descriptions
	wait__doc__ = "Number of turns to wait for."

	def __init__(self, sequence, \
					id,	slot, type, turns, resources, \
					wait):
		Order.__init__(self, sequence, \
					id, slot, type, turns, resources)

		self.length += 4
		self.wait = wait
		
	def __str__(self):
		output = Order.__str__(self)
		output += pack(self.substruct, self.wait)

		return output
