
from xstruct import pack

from Header import Processed

class Sequence(Processed):
	"""\
	The Sequence packet consists of:
		* A uint32 error code
	"""

	no = 2
	struct = "I"

	def __init__(self, sequence, number):
		if 1 > sequence:
			raise ValueError("Sequence is a reply packet so needs a valid sequence number (%i)" % sequence)
		Processed.__init__(self, sequence)

		self.number = number
	
	def pack(self):
		output = Processed.pack(self)
		output += pack(self.struct, self.number)

		return output

