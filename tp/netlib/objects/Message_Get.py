
from xstruct import pack

from Base import GetWithIDandSlot

class Message_Get(GetWithIDandSlot):
	"""\
	The Message_Get packet consists of:
		* A UInt32, board to get the message from.
		* a list of,
			* A SInt32, message slots
	"""
	no = 18
