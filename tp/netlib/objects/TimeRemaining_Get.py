
from xstruct import pack

from Header import Processed

class TimeRemaining_Get(Processed):
	"""\
	The TimeRemaining_Get packet is empty.
	"""
	no = 14
	struct = ""

	def __init__(self, sequence):
		Processed.__init__(self, sequence)

