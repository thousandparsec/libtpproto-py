
from xstruct import pack

from Get import GetSlot

class Message_Remove(GetSlot):
	"""\
	The Message_Remove packet consists of:
		* A UInt32, board to get the messages from.
		* a list of,
			* A SInt32, message slots
	"""
	no = 21
