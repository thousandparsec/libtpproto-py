
from xstruct import pack

from Get import GetSlot

class Order_Get(GetSlot):
	"""\
	The Order_Get packet consists of:
		* A UInt32, object to get the orders from.
		* a list of,
			* A SInt32, order slots
	"""
	no = 10
