
from xstruct import pack

from Header import Processed

class Order_Get(Processed):
	"""\
	The Order_Get packet consists of:
		* A UInt32, object to get the orders from.
		* a list of,
			* A UInt32, order slots
	"""

	no = 10
	struct = "I[I]"

	def __init__(self, sequence, id, slots):
		Processed.__init__(self, sequence)

		# Length is:
		#  * 4 bytes (uint32 - id)
		#
		self.length = 4 + 4 + 4 * len(slots)
	
		self.id = id
		self.slots = slots
	
	def __repr__(self):
		output = Processed.__repr__(self)
		output += pack(self.struct, self.id, self.slots)

		return output
