
from xstruct import pack

from Header import Processed

class Order_Remove(Processed):
	"""\
	The Order_Remove packet consists of:
		* A uint32, object to get the orders from.
		* A uint32, list ID of order slots.
	"""

	no = 13
	struct = "I[I]"

	def __init__(self, sequence, oid, slots):
		Processed.__init__(self, sequence)

		# Length is:
		#  * 4 bytes (uint32 - id)
		#
		self.length = 4 + 4 + 4 * len(slots)
	
		self.oid = oid
		self.slots = slots
	
	def __repr__(self):
		output = Processed.__repr__(self)
		output += pack(self.struct, self.oid, self.slots)

		return output
