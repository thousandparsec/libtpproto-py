
from xstruct import pack


from Description import Describable
from ObjectDesc import descriptions

class Order(Describable):
	"""\
	The Order packet consists of:

 The Order Description packet contains: int32 order type, string name, string description, int32 number of parameters and then of each parameter: string name, int32 type ID, string desc. The Parameter Types are given below:

	The OK packet consists of:
		* A string 
		(the string can be safely ignored - however it may 
		contain useful information for debugging purposes)
	"""

	no = 0
	struct = "S"

	def __init__(self, sequence, s=""):
		if 1 > sequence:
			raise ValueError("OK is a reply packet so needs a valid sequence number (%i)" % sequence)
		Processed.__init__(self, sequence)

		# Length is:
		#  * 4 bytes (32 bit integer)
		#  * the string
		#  * null terminator
		#
		self.length = 4 + len(s) + 1
		self.s = s
	
	def __repr__(self):
		output = Processed.__repr__(self)
		output += pack(self.struct, self.s)

		return output
