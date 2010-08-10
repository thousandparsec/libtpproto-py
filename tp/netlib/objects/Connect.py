
from xstruct import pack

from Header import Processed

class Connect(Processed):
	"""\
	The Connect packet consists of:
		* A String, may	contain useful information for stat purposes
	"""

	no = 3
	struct = "S"

	def __init__(self, sequence, s=""):
		Processed.__init__(self, sequence)

		self.s = s
	
	def pack(self):
		output = Processed.pack(self)
		output += pack(self.struct, self.s)

		return output
