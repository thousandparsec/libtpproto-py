
from xstruct import pack


from Description import Describable
from ObjectDesc import descriptions

class Order(Describable):
	"""\
 	An Order Packet or Insert Order packet.
	A Order packet consist of:

	* a UInt32, Object ID of the order is on/to be placed on
	* a UInt32, Slot number of the order/to be put in, 
		-1 will insert at the last position,
		otherwise it is inserted before the number
	* a UInt32, (Read Only) The number of turns the order will take
	* a list of
		* a UInt32, The resource ID
		* a UInt32, The units of that resource required
		
	* Extra data required by the order is appended to the end and is defined on a descriptions
	"""
	no = 11
	struct = "III [II]"

	def __init__(self, sequence, s=""):
		if 1 > sequence:
			raise ValueError("OK is a reply packet so needs a valid sequence number (%i)" % sequence)
		Processed.__init__(self, sequence)

		# Length is:
		#  * 4 bytes (32 bit integer)
		#  * the string
		#  * null terminator
		#
		self.length = 4 + len(s) + 1
		self.s = s
	
	def __repr__(self):
		output = Processed.__repr__(self)
		output += pack(self.struct, self.s)

		return output
