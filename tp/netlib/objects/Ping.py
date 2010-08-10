
from xstruct import pack

from Header import Processed

class Ping(Processed):
	"""\
	The Ping frame is empty and is only used to keep a connection alive that
	would possibly terminate otherwise. No more then 1 ping frame every 
	second should be sent and then only if no other data has been sent.
	"""
	no = 27
	struct = ""

	def __init__(self, sequence):
		Processed.__init__(self, sequence)
