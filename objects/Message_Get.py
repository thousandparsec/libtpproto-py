
from xstruct import pack

from Header import Processed

class Message_Get(Processed):
	"""\
	The Message_Get packet consists of:
		* A UInt32, board to get the message from.
		* a list of,
			* A UInt32, message slots
	"""

	no = 18
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
