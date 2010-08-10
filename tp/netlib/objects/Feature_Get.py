
from xstruct import pack

from Header import Processed

class Feature_Get(Processed):
	"""\
	The Get Features frame has no data. Get the features this server supports.
	This frame can be sent before Connect.
	"""
	no = 25
	struct = ""

	def __init__(self, sequence):
		Processed.__init__(self, sequence)
	
	def pack(self):
		output = Processed.pack(self)
		return output
