
from xstruct import pack, unpack

from Description import Describable
from OrderDesc import descriptions

class Order(Describable):
	"""\
 	An Order Packet or Insert Order packet.
	A Order packet consist of:

	* a UInt32, Object ID of the order is on/to be placed on
	* a UInt32, Order type ID
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
	struct = "IIII [II]"

	def __init__(self, sequence, \
			id,	type, slot, turns, resources, \
			*args, **kw):
		Describable.__init__(self, sequence)

		if kw.has_key('extra'):
			extra = kw['extra']
		else:
			extra = None
	
		# Upgrade the class to the real type
		# FIXME: The order/object class needs to be merged as this is all repeated
		if self.__class__ == Order or str(self.__class__).endswith("Order_Insert"):
			if descriptions().has_key(type):
				self.__class__ = descriptions()[type]

				if extra != None or len(args) > 0:
					if extra != None:
						if len(self.substruct) > 0:
							args, leftover = unpack(self.substruct, extra)
						else:
							args = None

					args = (self, sequence, id, type, slot, turns, resources,) + args
					apply(self.__class__.__init__, args)

				return
			else:
				# FIXME: Should throw a description error
				if extra != None:
					self.extra = extra

		self.length = \
			4 + 4 + 4 + 4 + \
			4 + len(resources)*(4+4)

		self.id = id
		self.type = type
		self.slot = slot
		self.turns = turns
		self.resources = resources

	def __repr__(self):
		output = Describable.__repr__(self)
		output += pack(self.struct, self.id, self.type, self.slot, self.turns, self.resources)

		return output
	
	def process_extra(self, extra):
		pass

