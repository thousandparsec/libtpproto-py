
from xstruct import pack
from objects import Order

class NOp(Order):
	"""\
	A do no nothing order.
	"""
	subtype = 0
	substruct = "I"

	def __init__(self, sequence, \
					id,	slot, turns, resources, \
					wait):
		Order.__init__(self, sequence, \
					id, slot, turns, resources,
					wait)

		self.length += 4
		self.wait = wait

	def __repr__(self):
		output = Object.__repr__(self)
		output += pack(self.substruct, self.wait)

		return output
