
from xstruct import pack

from Header import Processed

class TimeRemaining(Processed):
	"""\
	The TimeRemaining packet consists of:
		* UInt32, Seconds left till the turn ends.
	"""
	no = 15
	struct = "I"

	def __init__(self, sequence, time):
		Processed.__init__(self, sequence)

		# Length is:
		#  * 4 bytes UInt32
		#
		self.length = 4
		self.time = time
	
	def __repr__(self):
		output = Processed.__repr__(self)
		output += pack(self.struct, self.time)

		return output
