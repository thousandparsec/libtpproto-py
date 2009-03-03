
from xstruct import pack, unpack

from Description import Describable, DescriptionError
from ObjectDesc import descriptions

class Object(Describable):
	"""\
	The Object packet consists of:
		* a UInt32, object ID
		* a UInt32, object type
		* a String, name of object
		* a UInt64, size of object (diameter)
		* 3 by Int64, position of object
		* 3 by Int64, velocity of object
		* a list of UInt32, object IDs of objects contained in the current object
		* a list of UInt32, order types that the player can send to this object
		* a UInt32, number of orders currently on this object
		* a UInt64, the last modified time
		* 2 by UInt32 of padding, for future expansion of common attributes
		* extra data, as defined by each object type
	"""
	no = 7
	struct = "IIS Q 3q 3q [I] [I] I T 8x"

	_name = "Unknown Object"

	def __init__(self, sequence, \
			id, subtype, name, \
			size, \
			posx, posy, posz, \
			velx, vely, velz, \
			contains, \
			order_types, \
			order_number, \
			modify_time, \
			*args, **kw):
		Describable.__init__(self, sequence)

		self.length = \
			4 + 4 + \
			4 + len(name) + \
			8 + 3*8 + 3*8 + \
			4 + len(contains)*4 + \
			4 + len(order_types)*4 + \
			4 + 8 + 8

		self.id           = id
		self._subtype     = subtype
		self.name         = name
		self.size         = size
		self.pos          = (posx, posy, posz)
		self.vel          = (velx, vely, velz)
		self.contains     = contains
		self.order_types  = order_types
		self.order_number = order_number
		self.modify_time  = modify_time

		if self.__class__ == Object:
			try:
				if kw.has_key('force'):
					cls = kw['force']
				else:
					cls = descriptions()[subtype]
				self.__class__ = cls

				if len(args) > 0:
					self.__init__(sequence, \
									id, subtype, name, \
									size, \
									posx, posy, posz, \
									velx, vely, velz, \
									contains, \
									order_types, \
									order_number, \
									modify_time, *args)
			except KeyError, e:
				raise DescriptionError(sequence, subtype)

	def __str__(self):
		output = Describable.__str__(self)
		output += pack(self.struct, \
				self.id, \
				self._subtype, \
				self.name, \
				self.size, \
				self.pos[0], \
				self.pos[1], \
				self.pos[2], \
				self.vel[0], \
				self.vel[1], \
				self.vel[2], \
				self.contains, \
				self.order_types, \
				self.order_number, \
				self.modify_time)
		return output

	def __repr__(self):
		"""\
		Return a reconisable string.
		"""
		return "<%s @ %s>" % \
			(self.__class__.__name__, self.id)
		return "<%s @ %s (seq: %i length: %i)>" % \
			(self.__class__.__name__, hex(id(self)),
				self.sequence, self.length)
