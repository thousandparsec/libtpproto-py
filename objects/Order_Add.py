
from xstruct import pack

from Header import Processed

class Order_Add(Processed):
	"""\
	"""
	no = 12
	struct = "S"

	def __init__(self, sequence, s=""):
		Processed.__init__(self, sequence)

		# Length is:
		#  * 4 bytes (uint32 - string length)
		#  * the string
		#  * null terminator
		#
		self.length = 4 + len(s) + 1

		self.s = s
	
	def __repr__(self):
		output = Processed.__repr__(self)
		output += pack(self.struct, self.s)

		return output
