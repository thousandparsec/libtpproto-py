
from xstruct import pack

from Base import GetWithIDandSlot

class Message_Remove(GetWithIDandSlot):
	"""\
	The Message_Remove packet consists of:
		* A UInt32, board to get the messages from.
		* a list of,
			* A SInt32, message slots
	"""
	no = 21
