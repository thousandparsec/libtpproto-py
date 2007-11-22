
from xstruct import pack

from Header import Processed

class TurnFinished(Processed):
	"""\
	The TurnFinished packet consists of no data.
	"""
	no = 63
	struct = ""

	def __init__(self, sequence):
		Processed.__init__(self, sequence)

		self.length = 0
