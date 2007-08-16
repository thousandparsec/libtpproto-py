
from xstruct import pack

from Header import Processed

class Games_Get(Processed):
	"""\
	The Games_Get packet has no data.
	"""
	no = 65
	struct = ""
	
	def __init__(self, sequence):
		Processed.__init__(self, sequence)

		# Length is:
		#  * 4 bytes (uint32 - error code
		#  * 4 bytes (uint32 - string length)
		#  * the string
		#  * null terminator
		#
		self.length = 0

