
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
