
from xstruct import pack

from Header import Processed

class Fail(Processed):
	"""\
	The Fail packet consists of:
		* A uint32 error code
		* A string 
		(the string can be safely ignored - however it may 
		contain useful information for debugging purposes)
	"""

	no = 1
	struct = "IS"

	def __init__(self, sequence, errno, s=""):
		if sequence < 1:
			raise ValueError("Fail is a reply packet so needs a valid sequence number (%i)" % sequence)
		Processed.__init__(self, sequence)

		# Length is:
		#  * 4 bytes (uint32 - error code
		#  * 4 bytes (uint32 - string length)
		#  * the string
		#  * null terminator
		#
		self.length = 4 + 4 + len(s) + 1

		self.errno = errno
		self.s = s
	
	def __repr__(self):
		output = Processed.__repr__(self)
		output += pack(self.struct, self.errno, self.s)

		return output

