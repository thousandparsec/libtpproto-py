
from xstruct import pack

from Get import GetSlot

class Message_Get(GetSlot):
	"""\
	The Message_Get packet consists of:
		* A UInt32, board to get the message from.
		* a list of,
			* A SInt32, message slots
	"""
	no = 18
