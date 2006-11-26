
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

		# Length is:
		#  * 4 bytes (uint32 - error code
		#  * 4 bytes (uint32 - string length)
		#  * the string
		#  * null terminator
		#
		self.length = 4

		self.number = number
	
	def __str__(self):
		output = Processed.__str__(self)
		output += pack(self.struct, self.number)

		return output

