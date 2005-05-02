
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
		self.length = 0
	
	def __repr__(self):
		output = Processed.__repr__(self)
		return output
