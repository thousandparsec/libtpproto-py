
from xstruct import pack

from Header import Processed

class Ping(Processed):
	"""\
	"""
	no = 27
	struct = ""

	def __init__(self, sequence):
		Processed.__init__(self, sequence)
		self.length = 0
	
	def __repr__(self):
		return Processed.__repr__(self)
