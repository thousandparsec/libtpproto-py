
from xstruct import pack

from Get import GetSlot

class Order_Remove(GetSlot):
	"""\
	The Order_Remove packet consists of:
		* A UInt32, object to remove the orders from.
		* a list of,
			* A SInt32, order slots
	"""
	no = 13
