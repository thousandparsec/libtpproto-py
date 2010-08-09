
from xstruct import pack

from Header import Processed

class OrderQueue(Processed):
	"""\
	"""

	no = 75
	struct = "ITII[I]"

	def __init__(self, sequence, id, modify_time, maxslots, numorders, ordertypes):
		Processed.__init__(self, sequence)

		self.length = 4 + 8 + 4 + 4 + 4+len(ordertypes)*4
		self.id = id
		self.modify_time = modify_time
		self.maxslots = maxslots
		self.numorders = numorders
		self.ordertypes = ordertypes

		self.name = "Order Queue %i" % id
	
	def __str__(self):
		output = Processed.__str__(self)
		output += pack(self.struct, self.id, self.modify_time, self.maxslots, self.numorders, self.ordertypes)

		return output
