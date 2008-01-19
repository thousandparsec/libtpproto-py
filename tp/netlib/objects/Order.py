
from xstruct import pack, unpack

from Description import Describable, DescriptionError
from OrderDesc import descriptions

class Order(Describable):
	"""\
 	An Order Packet or Insert Order packet.
	The Order packet consists of:
		* a UInt32, Object ID of the order is on/to be placed on
		* a SInt32, Slot number of the order/to be put in, 
			-1 will insert at the last position,
			otherwise it is inserted before the number
		* a UInt32, Order type ID
		* a UInt32, (Read Only) The number of turns the order will take
		* a list of
			* a UInt32, The resource ID
			* a UInt32, The units of that resource required
		* extra data, as defined by each order type
	"""
	no = 11
	struct = "IjIj [II]"

	_name = "Unknown Order"

	def __init__(self, sequence, \
			id,	slot, subtype, turns, resources, *args, **kw):
		Describable.__init__(self, sequence)

		self.length = \
			4 + 4 + 4 + 4 + \
			4 + len(resources)*(4+4)

		self.id        = id
		self.slot      = slot
		self._subtype  = subtype
		self.turns     = turns
		self.resources = resources

		if self.__class__ == Order \
				or str(self.__class__.__name__).endswith("Order_Insert") \
				or str(self.__class__.__name__).endswith("Order_Probe"):
			try:
				if kw.has_key('force'):
					cls = kw['force']
					del kw['force']
				else:
					cls = descriptions()[subtype]

				self.__class__ = cls
				if len(args) > 0:
					self.__init__(sequence, id,	slot, subtype, turns, resources, *args, **kw)
			except KeyError, e:
				raise DescriptionError(sequence, subtype)

	def __str__(self):
		output = Describable.__str__(self)
		output += pack(self.struct, self.id, self.slot, self._subtype, self.turns, self.resources)
		return output

	def __repr__(self):
		"""\
		Return a reconisable string.
		"""
		return "<Order - %s @ %s (seq: %i length: %i)>" % \
			(self.__class__.__name__, hex(id(self)), self.sequence, self.length)

