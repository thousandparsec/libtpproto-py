
from xstruct import pack, unpack

from Description import Describable
from OrderDesc import descriptions

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

	def __init__(self, sequence, \
			id,	slot, turns, resources, \
			extra=None, *args):
		Describable.__init__(self, sequence)
		
		# Upgrade the class to the real type
		if self.__class__ == Order:
			if descriptions().has_key(type):
				self.__class__ = descriptions()[type]

				if extra != None or len(args) > 0:
					args = (extra,)+args
					if extra != None:
						if len(self.substruct) > 0:
							args, leftover = unpack(self.substruct, extra)

					args = (self, sequence, id, slot, turns, resources,) + args
					apply(self.__class__.__init__, args)

				return
			else:
				# FIXME: Should throw a description error
				if extra != None:
					self.extra = extra
		
		self.length = \
			4 + 4 + 4 + \
			4 + len(resources)*(4+4)

		self.id = id
		self.slot = slot
		self.turns = turns
		self.resources = resources

	def __repr__(self):
		output = Describable.__repr__(self)
		output += pack(self.struct, self.id, self.slot, self.turns, self.resources)

		return output
