
from xstruct import pack, unpack

from Description import Describable, DescriptionError
from OrderDesc import descriptions

class Order(Describable):
	"""\
 	An Order Packet or Insert Order packet.
	A Order packet consist of:

	* a UInt32, Object ID of the order is on/to be placed on
	* a SInt32, Slot number of the order/to be put in, 
		-1 will insert at the last position,
		otherwise it is inserted before the number
	* a UInt32, Order type ID
	* a UInt32, (Read Only) The number of turns the order will take
	* a list of
		* a UInt32, The resource ID
		* a UInt32, The units of that resource required
		
	* Extra data required by the order is appended to the end and is defined on a descriptions
	"""
	no = 11
	struct = "IjII [II]"

	def __init__(self, sequence, \
			id,	slot, type, turns, resources, \
			*args, **kw):
		Describable.__init__(self, sequence)

		if kw.has_key('extra'):
			extra = kw['extra']
		else:
			extra = None
	
		# Upgrade the class to the real type
		# FIXME: The order/object class needs to be merged as this is all repeated
		if self.__class__ == Order \
				or str(self.__class__.__name__).endswith("Order_Insert") \
				or str(self.__class__.__name__).endswith("Order_Probe"):
			if descriptions().has_key(type):
				self.__class__ = descriptions()[type]

				if extra != None or len(args) > 0:
					if extra != None:
						if len(self.substruct) > 0:
							args, leftover = unpack(self.substruct, extra)
						else:
							args = ()

				args = (self, sequence, id, slot, type, turns, resources,) + args
				apply(self.__class__.__init__, args)

				return

		self.length = \
			4 + 4 + 4 + 4 + \
			4 + len(resources)*(4+4)

		self.id = id
		self.type = type
		self.slot = slot
		self.turns = turns
		self.resources = resources

		if not descriptions().has_key(type):
			if extra != None:
				self.length += len(extra)
				raise DescriptionError("No description for order type %s." % type)
			
	def __repr__(self):
		output = Describable.__repr__(self)
		output += pack(self.struct, self.id, self.slot, self.type, self.turns, self.resources)

		return output
	
	def process_extra(self, extra):
		pass

